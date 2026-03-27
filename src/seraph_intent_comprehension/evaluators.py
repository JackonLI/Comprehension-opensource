from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from seraph_intent_comprehension.clients import BaseLLMClient
from seraph_intent_comprehension.datasets import (
    DatasetSpec,
    default_output_path,
    load_dataset_frame,
    prompt_for_mode,
)
from seraph_intent_comprehension.prompts import (
    load_base_prompt,
    load_prompt_with_snmt,
    load_snmt_slices,
)


LOGGER = logging.getLogger(__name__)
INCOMPLETE_MARKERS = ("incomplete", "not found")


@dataclass(frozen=True)
class EvaluationTotals:
    input_tokens: int
    output_tokens: int
    llm_calls: int


def build_basic_messages(
    prompt: str,
    intent_text: str,
    extra_user_text: str = "",
) -> list[dict[str, str]]:
    user_content = str(intent_text)
    if extra_user_text:
        user_content = f"{user_content}{extra_user_text}"
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_content},
    ]


def is_incomplete_response(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in INCOMPLETE_MARKERS)


def generate_iterative_ir(
    *,
    client: BaseLLMClient,
    model: str,
    base_prompt: str,
    snmt_slices: list[str],
    intent_text: str,
    extra_user_text: str = "",
) -> tuple[str, int, int]:
    previous_output = ""
    final_output = ""
    token_cost_total = 0
    llm_calls = 0

    for slice_number, snmt_slice in enumerate(snmt_slices, start=1):
        prompt = (
            "# Incomplete IR generated last round:\n"
            f"{previous_output}"
            f"{base_prompt}\n"
            f"# SNMT Slice {slice_number}\n"
            f"{snmt_slice}"
        )
        response = client.request(
            build_basic_messages(prompt, str(intent_text), extra_user_text),
            model,
        )
        llm_calls += 1
        token_cost_total += response.total_tokens
        final_output = response.content.strip()
        if is_incomplete_response(final_output):
            previous_output = f"{final_output}\n"
            continue
        break

    return final_output, token_cost_total, llm_calls


def evaluate_dataset(
    *,
    client: BaseLLMClient,
    repo_root: Path,
    data_root: Path,
    output_root: Path,
    spec: DatasetSpec,
    model: str,
    mode: str,
    experiment_name: str,
    prompt_override: Optional[str] = None,
    snmt_slice_size: int = 900,
) -> tuple[Path, EvaluationTotals]:
    dataframe = load_dataset_frame(data_root, spec).copy()
    selected_prompt = prompt_override or prompt_for_mode(spec, mode)

    total_input_tokens = 0
    total_output_tokens = 0
    total_llm_calls = 0
    real_outputs: list[str] = []
    time_costs: list[float] = []
    token_costs: list[int] = []

    LOGGER.info(
        "Evaluating %s/%s with mode=%s model=%s",
        spec.topology,
        spec.task_type,
        mode,
        model,
    )

    if mode in {"basic", "baseline"}:
        prompt = load_prompt_with_snmt(repo_root, selected_prompt, spec.snmt_file)
        for intent_text in dataframe["NL intent"]:
            start_time = time.time()
            response = client.request(build_basic_messages(prompt, str(intent_text)), model)
            time_costs.append(time.time() - start_time)
            real_outputs.append(response.content)
            token_costs.append(response.total_tokens)
            total_input_tokens += response.prompt_tokens
            total_output_tokens += response.completion_tokens
            total_llm_calls += 1
    elif mode == "iterative":
        base_prompt = load_base_prompt(repo_root, selected_prompt)
        snmt_slices = load_snmt_slices(repo_root, spec.snmt_file, snmt_slice_size)
        for intent_text in dataframe["NL intent"]:
            start_time = time.time()
            final_output, token_cost_total, llm_calls = generate_iterative_ir(
                client=client,
                model=model,
                base_prompt=base_prompt,
                snmt_slices=snmt_slices,
                intent_text=str(intent_text),
            )
            time_costs.append(time.time() - start_time)
            real_outputs.append(final_output)
            token_costs.append(token_cost_total)
            total_llm_calls += llm_calls
    else:
        raise ValueError(f"Unsupported evaluation mode: {mode}")

    dataframe["Real Output"] = real_outputs
    dataframe["Time Cost (s)"] = time_costs
    dataframe["Token Cost"] = token_costs

    output_path = default_output_path(output_root, experiment_name, mode, model, spec)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_excel(output_path, index=False)
    LOGGER.info("Saved results to %s", output_path)

    return output_path, EvaluationTotals(
        input_tokens=total_input_tokens,
        output_tokens=total_output_tokens,
        llm_calls=total_llm_calls,
    )

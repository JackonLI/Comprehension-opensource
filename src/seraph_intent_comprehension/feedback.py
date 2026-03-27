from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Optional

import pandas as pd

from seraph_intent_comprehension.clients import BaseLLMClient
from seraph_intent_comprehension.datasets import DatasetSpec, prompt_for_mode
from seraph_intent_comprehension.evaluators import generate_iterative_ir
from seraph_intent_comprehension.prompts import load_base_prompt, load_snmt_slices


ERROR_TYPE_OPTIONS = [
    "Wrong endpoint name",
    "Wrong interface/prefix",
    "Wrong application",
    "Others",
]


def _is_correct_value(value: object) -> bool:
    lowered = str(value).strip().lower()
    return lowered in {"1", "1.0", "true", "yes", "y"}


def _has_non_empty_values(series: pd.Series) -> bool:
    return any(str(value).strip() not in {"", "nan", "None"} for value in series)


def select_annotation_column(dataframe: pd.DataFrame) -> str:
    if "Expert Correctness" in dataframe.columns and _has_non_empty_values(dataframe["Expert Correctness"]):
        return "Expert Correctness"
    if "Correctness" in dataframe.columns:
        return "Correctness"
    raise ValueError(
        "No usable correctness column found. Run the automatic scorer first or "
        "add manual review annotations under 'Expert Correctness'."
    )


def _default_output_path(result_file: Path) -> Path:
    return result_file.with_name(f"{result_file.stem}_feedback.xlsx")


def _prompt_user(prompt: str, default: Optional[str] = None) -> str:
    suffix = f" [{default}]" if default else ""
    response = input(f"{prompt}{suffix}: ").strip()
    return response or (default or "")


def _prompt_error_type(default: Optional[str] = None) -> str:
    print("Error types:")
    for index, label in enumerate(ERROR_TYPE_OPTIONS, start=1):
        print(f"  {index}. {label}")
    default_value = default if default in ERROR_TYPE_OPTIONS else None
    while True:
        response = _prompt_user("Enter the error type number or label", default_value)
        if response in ERROR_TYPE_OPTIONS:
            return response
        if response.isdigit():
            numeric_value = int(response)
            if 1 <= numeric_value <= len(ERROR_TYPE_OPTIONS):
                return ERROR_TYPE_OPTIONS[numeric_value - 1]
        print("Invalid error type, please try again.")


def run_feedback_session(
    *,
    client: BaseLLMClient,
    repo_root: Path,
    result_file: Path,
    output_file: Path,
    spec: DatasetSpec,
    model: str,
    feedback_prompt_mode: str,
    snmt_slice_size: int = 900,
    max_samples: int = 30,
    max_rounds: int = 4,
    random_seed: int = 42,
) -> Path:
    dataframe = pd.read_excel(result_file)
    annotation_column = select_annotation_column(dataframe)
    incorrect_samples = dataframe[
        ~dataframe[annotation_column].apply(_is_correct_value)
    ].copy()
    if incorrect_samples.empty:
        raise ValueError(
            f"No incorrect rows found in {result_file} using column '{annotation_column}'."
        )

    if len(incorrect_samples) > max_samples:
        incorrect_samples = incorrect_samples.sample(n=max_samples, random_state=random_seed)

    base_prompt = load_base_prompt(
        repo_root,
        prompt_for_mode(spec, feedback_prompt_mode),
    )
    snmt_slices = load_snmt_slices(repo_root, spec.snmt_file, snmt_slice_size)

    if output_file.exists():
        feedback_dataframe = pd.read_excel(output_file)
    else:
        feedback_dataframe = pd.DataFrame(
            columns=[
                "Source Output File",
                "Row Index",
                "Annotation Column",
                "NL intent",
                "Expected IR",
                "Original Output",
                "Error Type",
                "Feedback",
                "Revised Output",
                "Accepted",
                "Rounds",
                "Time Taken (s)",
            ]
        )

    for row_index, row in incorrect_samples.iterrows():
        input_intent = str(row["NL intent"])
        expected_ir = str(row["Expected IR"])
        current_output = str(row.get("Real Output", ""))
        suggested_error_type = str(row.get("Expert Error Type", "")).strip() or None
        suggested_notes = str(row.get("Expert Notes", "")).strip() or None

        print("=" * 80)
        print(f"Processing row {row_index}")
        print(f"Intent: {input_intent}")
        print(f"Expected IR: {expected_ir}")
        print(f"Current output: {current_output}")
        if suggested_notes:
            print(f"Expert notes: {suggested_notes}")

        accepted = False
        round_count = 1
        latest_feedback = suggested_notes or ""
        latest_error_type = suggested_error_type or ERROR_TYPE_OPTIONS[-1]
        latest_revised_output = current_output
        start_time = time.time()

        while round_count <= max_rounds:
            print(f"Round {round_count}/{max_rounds}")
            latest_error_type = _prompt_error_type(latest_error_type)
            latest_feedback = _prompt_user(
                "Enter expert feedback for this row",
                latest_feedback,
            )
            feedback_text = (
                "In last try, you generated the following IR:\n"
                f"{latest_revised_output}\n"
                "It is incorrect because:\n"
                f"{latest_feedback}\n"
                "Please try again."
            )
            latest_revised_output, _, _ = generate_iterative_ir(
                client=client,
                model=model,
                base_prompt=base_prompt,
                snmt_slices=snmt_slices,
                intent_text=input_intent,
                extra_user_text=f"\n# Human feedback for this intent:\n{feedback_text}\n",
            )
            print("\nRevised output:\n")
            print(latest_revised_output)
            decision = _prompt_user("Accept this revised output? (y/n)", "n").lower()
            if decision == "y":
                accepted = True
                break
            round_count += 1

        feedback_row = {
            "Source Output File": str(result_file),
            "Row Index": row_index,
            "Annotation Column": annotation_column,
            "NL intent": input_intent,
            "Expected IR": expected_ir,
            "Original Output": row.get("Real Output", ""),
            "Error Type": latest_error_type,
            "Feedback": latest_feedback,
            "Revised Output": latest_revised_output,
            "Accepted": accepted,
            "Rounds": min(round_count, max_rounds),
            "Time Taken (s)": time.time() - start_time,
        }
        feedback_dataframe = pd.concat(
            [feedback_dataframe, pd.DataFrame([feedback_row])],
            ignore_index=True,
        )
        feedback_dataframe.to_excel(output_file, index=False)

    return output_file


def resolve_feedback_output_file(result_file: Path, explicit_output: Optional[str]) -> Path:
    if explicit_output:
        return Path(explicit_output).expanduser().resolve()
    return _default_output_path(result_file)

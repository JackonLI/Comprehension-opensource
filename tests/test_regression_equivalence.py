from __future__ import annotations

import ast
import asyncio
import os
import tempfile
import types
import unittest
from pathlib import Path

import pandas as pd

from seraph_intent_comprehension.datasets import get_dataset_spec
from seraph_intent_comprehension.evaluators import evaluate_dataset, generate_iterative_ir
from seraph_intent_comprehension.postprocess import compare_json_content, parse_json_text
from seraph_intent_comprehension.prompts import load_base_prompt, load_prompt_with_snmt, load_snmt_slices


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT.parent / "comprehension_result"


class FakeResponse:
    def __init__(self, content: str, prompt_tokens: int, completion_tokens: int) -> None:
        self.content = content
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class FakeClient:
    def request(self, messages: list[dict[str, str]], model: str) -> FakeResponse:
        prompt = messages[0]["content"]
        user_input = messages[1]["content"]
        if "# SNMT Slice 1" in prompt:
            response = "incomplete"
            prompt_tokens = 10
            completion_tokens = 0
        elif "# SNMT Slice 2" in prompt:
            response = f"FINAL::{user_input}"
            prompt_tokens = 20
            completion_tokens = 0
        else:
            response = f"BASIC::{user_input}"
            prompt_tokens = len(prompt)
            completion_tokens = len(response)
        return FakeResponse(
            content=response,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )


def _load_legacy_functions(file_path: Path, function_names: set[str], namespace: dict) -> dict:
    source = file_path.read_text(encoding="utf-8")
    module = ast.parse(source, filename=str(file_path))
    selected_nodes = [
        node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in function_names
    ]
    selected_module = ast.Module(body=selected_nodes, type_ignores=[])
    compiled = compile(selected_module, str(file_path), "exec")
    exec(compiled, namespace)
    return namespace


class RegressionEquivalenceTests(unittest.TestCase):
    def test_basic_prompt_loading_matches_legacy(self) -> None:
        legacy_namespace = _load_legacy_functions(
            SOURCE_ROOT / "comprehension_eval_baseline.py",
            {"load_prompt"},
            {},
        )
        legacy_load_prompt = legacy_namespace["load_prompt"]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "prompts").mkdir()
            (temp_root / "snmt").mkdir()
            prompt_file = "prompt_basic.txt"
            snmt_file = "SNMT_campus_net.txt"
            (temp_root / "prompts" / prompt_file).write_text(
                (REPO_ROOT / "prompts" / prompt_file).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (temp_root / "snmt" / snmt_file).write_text(
                (REPO_ROOT / "snmt" / snmt_file).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            current_cwd = Path.cwd()
            os.chdir(temp_root)
            try:
                legacy_prompt = legacy_load_prompt(prompt_file, snmt_file)
            finally:
                os.chdir(current_cwd)

        new_prompt = load_prompt_with_snmt(REPO_ROOT, prompt_file, snmt_file)
        self.assertEqual(legacy_prompt.strip(), new_prompt.strip())

    def test_iterative_generation_matches_legacy(self) -> None:
        async def fake_send_remote_chat_api_call(messages, need_count_tokens=True, model=None):
            prompt = messages[0]["content"]
            user_input = messages[1]["content"]
            if "# SNMT Slice 1" in prompt:
                return "incomplete", 10
            return f"FINAL::{user_input}", 20

        legacy_namespace = _load_legacy_functions(
            SOURCE_ROOT / "comprehension_eval_localhost.py",
            {"intent_understanding_iterative"},
            {
                "asyncio": asyncio,
                "send_remote_chat_api_call": fake_send_remote_chat_api_call,
                "time": types.SimpleNamespace(time=lambda: 0),
                "logger": types.SimpleNamespace(info=lambda *args, **kwargs: None, debug=lambda *args, **kwargs: None),
            },
        )
        legacy_iterative = legacy_namespace["intent_understanding_iterative"]

        base_prompt = load_base_prompt(REPO_ROOT, "prompt_iterative.txt")
        snmt_slices = load_snmt_slices(REPO_ROOT, "SNMT_extreme_net.txt", 900)

        legacy_output, _, legacy_tokens = legacy_iterative(
            "sample intent",
            base_prompt,
            iter(snmt_slices),
            "gpt-4o",
        )
        (
            new_output,
            new_tokens,
            new_input_tokens,
            new_output_tokens,
            new_calls,
        ) = generate_iterative_ir(
            client=FakeClient(),
            model="gpt-4o",
            base_prompt=base_prompt,
            snmt_slices=snmt_slices,
            intent_text="sample intent",
        )

        self.assertEqual(legacy_output, new_output)
        self.assertEqual(legacy_tokens, new_tokens)
        self.assertEqual(new_input_tokens, 30)
        self.assertEqual(new_output_tokens, 0)
        self.assertEqual(new_calls, 2)

    def test_basic_evaluation_matches_legacy_outputs(self) -> None:
        spec = get_dataset_spec("campus_net", "intent")

        def legacy_intent_understanding(input_intent, prompt, model):
            response = f"BASIC::{input_intent}"
            return response, 0.5, len(prompt) + len(response)

        legacy_namespace = _load_legacy_functions(
            SOURCE_ROOT / "comprehension_eval_localhost.py",
            {"load_prompt", "evaluate_dataset"},
            {
                "pd": pd,
                "os": os,
                "intent_understanding": legacy_intent_understanding,
                "logging": types.SimpleNamespace(
                    info=lambda *args, **kwargs: None,
                    debug=lambda *args, **kwargs: None,
                ),
            },
        )
        legacy_evaluate = legacy_namespace["evaluate_dataset"]

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            (temp_root / "dataset" / "campus_net").mkdir(parents=True)
            (temp_root / "prompts").mkdir()
            (temp_root / "snmt").mkdir()

            source_df = pd.read_excel(REPO_ROOT / "intent dataset" / spec.relative_path).head(3)
            source_df.to_excel(temp_root / "dataset" / spec.relative_path, index=False)
            for prompt_name in {spec.basic_prompt}:
                (temp_root / "prompts" / prompt_name).write_text(
                    (REPO_ROOT / "prompts" / prompt_name).read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
            (temp_root / "snmt" / spec.snmt_file).write_text(
                (REPO_ROOT / "snmt" / spec.snmt_file).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            current_cwd = Path.cwd()
            os.chdir(temp_root)
            try:
                legacy_evaluate(
                    spec.relative_path,
                    spec.basic_prompt,
                    spec.snmt_file,
                    "legacy_output",
                    "gpt-4o",
                )
            finally:
                os.chdir(current_cwd)

            new_output_path, _ = evaluate_dataset(
                client=FakeClient(),
                repo_root=temp_root,
                data_root=temp_root / "dataset",
                output_root=temp_root / "outputs",
                spec=spec,
                model="gpt-4o",
                mode="basic",
                experiment_name="comparison",
            )

            legacy_df = pd.read_excel(temp_root / "legacy_output" / spec.relative_path)
            new_df = pd.read_excel(new_output_path)

        self.assertListEqual(list(legacy_df["Real Output"]), list(new_df["Real Output"]))
        self.assertListEqual(list(legacy_df["Token Cost"]), list(new_df["Token Cost"]))
        self.assertListEqual(list(legacy_df["NL intent"]), list(new_df["NL intent"]))

    def test_postprocess_matches_legacy(self) -> None:
        legacy_namespace = _load_legacy_functions(
            SOURCE_ROOT / "result_process.py",
            {"parse_json_text", "compare_json_content"},
            {"json": __import__("json")},
        )
        legacy_parse_json_text = legacy_namespace["parse_json_text"]
        legacy_compare_json_content = legacy_namespace["compare_json_content"]

        expected = '{"source":["a",["s"]],"destination":["b",["d"]],"application":["http"],"time":["any"],"action":"Permit"}'
        actual = expected

        legacy_expected, legacy_ok_expected = legacy_parse_json_text(expected)
        legacy_actual, legacy_ok_actual = legacy_parse_json_text(actual)
        new_expected, new_ok_expected = parse_json_text(expected)
        new_actual, new_ok_actual = parse_json_text(actual)

        self.assertEqual((legacy_ok_expected, legacy_ok_actual), (new_ok_expected, new_ok_actual))
        self.assertEqual(legacy_expected, new_expected)
        self.assertEqual(legacy_actual, new_actual)
        self.assertEqual(
            legacy_compare_json_content(legacy_expected, legacy_actual),
            compare_json_content(new_expected, new_actual),
        )


if __name__ == "__main__":
    unittest.main()

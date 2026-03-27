from __future__ import annotations

import argparse
import logging
from pathlib import Path

from seraph_intent_comprehension.clients import build_client
from seraph_intent_comprehension.config import (
    load_runtime_config,
    repo_root,
    resolve_data_root,
)
from seraph_intent_comprehension.datasets import get_dataset_spec, list_dataset_specs
from seraph_intent_comprehension.evaluators import evaluate_dataset
from seraph_intent_comprehension.feedback import (
    resolve_feedback_output_file,
    run_feedback_session,
)
from seraph_intent_comprehension.postprocess import (
    prepare_manual_review_directory,
    prepare_manual_review_file,
    score_directory,
    score_excel_file,
)


def _configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def _build_eval_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run Seraph intent comprehension evaluation."
    )
    parser.add_argument("--provider", choices=["openai", "ws"], default="openai")
    parser.add_argument("--model", required=True)
    parser.add_argument("--mode", choices=["basic", "iterative", "baseline"], required=True)
    parser.add_argument("--topology", choices=["campus_net", "cloud_net", "extreme"])
    parser.add_argument("--task", choices=["intent", "protect"])
    parser.add_argument("--all-datasets", action="store_true")
    parser.add_argument(
        "--prompt-file",
        help="Optional prompt override from the prompts directory.",
    )
    parser.add_argument("--experiment-name", default="default")
    parser.add_argument("--data-root", help="Override dataset root path.")
    parser.add_argument("--output-root", help="Override output root path.")
    parser.add_argument("--api-base-url", help="OpenAI-compatible base URL.")
    parser.add_argument("--ws-url", help="WebSocket gateway URL.")
    parser.add_argument("--slice-size", type=int, default=900)
    parser.add_argument("--list-datasets", action="store_true")
    return parser


def _build_score_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the automatic structural checker for Seraph intent outputs."
    )
    parser.add_argument(
        "--target",
        default=str(repo_root() / "outputs"),
        help="Excel file or directory to score in place.",
    )
    return parser


def _build_review_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare Excel outputs for expert manual review."
    )
    parser.add_argument(
        "--target",
        default=str(repo_root() / "outputs"),
        help="Excel file or directory to augment with manual review columns.",
    )
    return parser


def _build_feedback_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the interactive expert-feedback loop for incorrect outputs."
    )
    parser.add_argument("--provider", choices=["openai", "ws"], default="openai")
    parser.add_argument("--model", required=True)
    parser.add_argument("--topology", choices=["campus_net", "cloud_net", "extreme"], required=True)
    parser.add_argument("--task", choices=["intent", "protect"], required=True)
    parser.add_argument("--result-file", required=True, help="Scored or manually reviewed output file.")
    parser.add_argument(
        "--feedback-prompt-mode",
        choices=["iterative", "baseline", "basic"],
        default="iterative",
    )
    parser.add_argument("--output-file", help="Destination Excel file for feedback sessions.")
    parser.add_argument("--api-base-url", help="OpenAI-compatible base URL.")
    parser.add_argument("--ws-url", help="WebSocket gateway URL.")
    parser.add_argument("--slice-size", type=int, default=900)
    parser.add_argument("--max-samples", type=int, default=30)
    parser.add_argument("--max-rounds", type=int, default=4)
    return parser


def _selected_specs(args: argparse.Namespace) -> list:
    if args.list_datasets:
        for spec in list_dataset_specs():
            print(f"{spec.topology}/{spec.task_type}: {spec.relative_path}")
        return []
    if args.all_datasets:
        return list_dataset_specs()
    if not args.topology or not args.task:
        raise SystemExit("Specify --topology and --task, or use --all-datasets.")
    return [get_dataset_spec(args.topology, args.task)]


def main() -> None:
    parser = _build_eval_parser()
    args = parser.parse_args()

    runtime = load_runtime_config(
        provider=args.provider,
        model=args.model,
        api_base_url=args.api_base_url,
        ws_url=args.ws_url,
    )
    _configure_logging(runtime.log_level)

    specs = _selected_specs(args)
    if not specs:
        return

    client = build_client(runtime)
    resolved_repo_root = repo_root()
    data_root = resolve_data_root(args.data_root)
    output_root = (
        Path(args.output_root).expanduser().resolve()
        if args.output_root
        else resolved_repo_root / "outputs"
    )

    grand_total_input = 0
    grand_total_output = 0
    grand_total_calls = 0
    for spec in specs:
        output_path, totals = evaluate_dataset(
            client=client,
            repo_root=resolved_repo_root,
            data_root=data_root,
            output_root=output_root,
            spec=spec,
            model=args.model,
            mode=args.mode,
            experiment_name=args.experiment_name,
            prompt_override=args.prompt_file,
            snmt_slice_size=args.slice_size,
        )
        grand_total_input += totals.input_tokens
        grand_total_output += totals.output_tokens
        grand_total_calls += totals.llm_calls
        print(f"Saved: {output_path}")

    print(f"Total LLM calls: {grand_total_calls}")
    print(f"Total prompt tokens: {grand_total_input}")
    print(f"Total completion tokens: {grand_total_output}")


def score_main() -> None:
    parser = _build_score_parser()
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()

    if target.is_file():
        updated = score_excel_file(target)
        print(f"Scored: {updated}")
        return

    if target.is_dir():
        updated_files = score_directory(target)
        print(f"Scored {len(updated_files)} files under {target}")
        return

    raise SystemExit(f"Target does not exist: {target}")


def review_main() -> None:
    parser = _build_review_parser()
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()

    if target.is_file():
        updated = prepare_manual_review_file(target)
        print(f"Prepared manual review sheet: {updated}")
        return

    if target.is_dir():
        updated_files = prepare_manual_review_directory(target)
        print(f"Prepared {len(updated_files)} manual review sheets under {target}")
        return

    raise SystemExit(f"Target does not exist: {target}")


def feedback_main() -> None:
    parser = _build_feedback_parser()
    args = parser.parse_args()

    runtime = load_runtime_config(
        provider=args.provider,
        model=args.model,
        api_base_url=args.api_base_url,
        ws_url=args.ws_url,
    )
    _configure_logging(runtime.log_level)

    resolved_repo_root = repo_root()
    spec = get_dataset_spec(args.topology, args.task)
    result_file = Path(args.result_file).expanduser().resolve()
    output_file = resolve_feedback_output_file(result_file, args.output_file)
    client = build_client(runtime)

    updated_file = run_feedback_session(
        client=client,
        repo_root=resolved_repo_root,
        result_file=result_file,
        output_file=output_file,
        spec=spec,
        model=args.model,
        feedback_prompt_mode=args.feedback_prompt_mode,
        snmt_slice_size=args.slice_size,
        max_samples=args.max_samples,
        max_rounds=args.max_rounds,
    )
    print(f"Saved feedback session: {updated_file}")

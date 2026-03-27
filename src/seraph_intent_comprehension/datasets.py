from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_INPUT_COLUMNS = ("NL intent", "Expected IR")


@dataclass(frozen=True)
class DatasetSpec:
    topology: str
    task_type: str
    relative_path: str
    basic_prompt: str
    iterative_prompt: str
    baseline_prompt: str
    snmt_file: str

    @property
    def dataset_stem(self) -> str:
        return Path(self.relative_path).stem


DATASET_REGISTRY: dict[tuple[str, str], DatasetSpec] = {
    ("campus_net", "intent"): DatasetSpec(
        topology="campus_net",
        task_type="intent",
        relative_path="campus_net/intent_campus.xlsx",
        basic_prompt="prompt_basic.txt",
        iterative_prompt="prompt_iterative.txt",
        baseline_prompt="prompt_baseline.txt",
        snmt_file="SNMT_campus_net.txt",
    ),
    ("campus_net", "protect"): DatasetSpec(
        topology="campus_net",
        task_type="protect",
        relative_path="campus_net/protect_campus.xlsx",
        basic_prompt="prompt_protect.txt",
        iterative_prompt="prompt_protect_iterative.txt",
        baseline_prompt="prompt_baseline.txt",
        snmt_file="SNMT_campus_net.txt",
    ),
    ("cloud_net", "intent"): DatasetSpec(
        topology="cloud_net",
        task_type="intent",
        relative_path="cloud_net/intent_cloud.xlsx",
        basic_prompt="prompt_basic.txt",
        iterative_prompt="prompt_iterative.txt",
        baseline_prompt="prompt_baseline.txt",
        snmt_file="SNMT_cloud_net.txt",
    ),
    ("cloud_net", "protect"): DatasetSpec(
        topology="cloud_net",
        task_type="protect",
        relative_path="cloud_net/protect_cloud.xlsx",
        basic_prompt="prompt_protect.txt",
        iterative_prompt="prompt_protect_iterative.txt",
        baseline_prompt="prompt_baseline.txt",
        snmt_file="SNMT_cloud_net.txt",
    ),
    ("extreme", "intent"): DatasetSpec(
        topology="extreme",
        task_type="intent",
        relative_path="extreme/intent_extreme.xlsx",
        basic_prompt="prompt_basic.txt",
        iterative_prompt="prompt_iterative.txt",
        baseline_prompt="prompt_baseline.txt",
        snmt_file="SNMT_extreme_net.txt",
    ),
    ("extreme", "protect"): DatasetSpec(
        topology="extreme",
        task_type="protect",
        relative_path="extreme/protect_extreme.xlsx",
        basic_prompt="prompt_protect.txt",
        iterative_prompt="prompt_protect_iterative.txt",
        baseline_prompt="prompt_baseline.txt",
        snmt_file="SNMT_extreme_net.txt",
    ),
}


def list_dataset_specs() -> list[DatasetSpec]:
    return list(DATASET_REGISTRY.values())


def get_dataset_spec(topology: str, task_type: str) -> DatasetSpec:
    try:
        return DATASET_REGISTRY[(topology, task_type)]
    except KeyError as exc:
        raise ValueError(f"Unsupported dataset combination: {topology}/{task_type}") from exc


def resolve_dataset_path(data_root: Path, spec: DatasetSpec) -> Path:
    dataset_path = data_root / spec.relative_path
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file does not exist: {dataset_path}")
    return dataset_path


def load_dataset_frame(data_root: Path, spec: DatasetSpec) -> pd.DataFrame:
    dataset_path = resolve_dataset_path(data_root, spec)
    dataframe = pd.read_excel(dataset_path)
    missing_columns = [
        column for column in REQUIRED_INPUT_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(
            f"Dataset {dataset_path} is missing required columns: {missing_columns}"
        )
    return dataframe


def prompt_for_mode(spec: DatasetSpec, mode: str) -> str:
    if mode == "basic":
        return spec.basic_prompt
    if mode == "iterative":
        return spec.iterative_prompt
    if mode == "baseline":
        return spec.baseline_prompt
    raise ValueError(f"Unsupported evaluation mode: {mode}")


def safe_model_name(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", model)


def default_output_path(
    output_root: Path,
    experiment_name: str,
    mode: str,
    model: str,
    spec: DatasetSpec,
) -> Path:
    return (
        output_root
        / experiment_name
        / mode
        / safe_model_name(model)
        / spec.topology
        / f"{spec.dataset_stem}_results.xlsx"
    )

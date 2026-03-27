from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd


MANUAL_REVIEW_COLUMNS = [
    "Expert Correctness",
    "Expert Error Type",
    "Expert Notes",
]


def extract_first_json_object(text: str) -> Optional[str]:
    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def parse_json_text(text: str) -> Tuple[Optional[dict], bool]:
    normalized = text.replace("{{", "{").replace("}}", "}").replace("\n", "").replace("\t", "")
    start = normalized.find("{")
    end = normalized.find("}", start)
    if start == -1 or end == -1:
        return None, False
    json_candidate = normalized[start : end + 1]
    try:
        return json.loads(json_candidate), True
    except json.JSONDecodeError:
        return None, False


def compare_json_content(expected: dict, actual: dict) -> tuple[int, str]:
    if not isinstance(expected, dict) or not isinstance(actual, dict):
        return 0, "wrong format"
    try:
        if expected["source"][0] != actual["source"][0] or expected["destination"][0] != actual["destination"][0]:
            return 0, "wrong endpoint name"
        if expected["source"][1] != actual["source"][1] or expected["destination"][1] != actual["destination"][1]:
            return 0, "wrong gateway or interface"
        if expected["application"] != actual["application"]:
            return 0, "wrong application"
        if expected["time"] != actual["time"]:
            return 0, "wrong time"
        if expected["action"] != actual["action"]:
            return 0, "wrong action"
        return 1, "ok"
    except (KeyError, IndexError, TypeError):
        return -1, "wrong format"


def score_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    required_columns = {"Expected IR", "Real Output"}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Missing columns required for scoring: {sorted(missing_columns)}")

    correctness_scores: list[int] = []
    error_analysis: list[str] = []
    for _, row in dataframe.iterrows():
        expected_json, expected_ok = parse_json_text(str(row["Expected IR"]))
        actual_json, actual_ok = parse_json_text(str(row["Real Output"]))
        if expected_ok and actual_ok:
            score, analysis = compare_json_content(expected_json, actual_json)
        else:
            score, analysis = 0, "invalid parse"
        correctness_scores.append(score)
        error_analysis.append(analysis)

    scored_dataframe = dataframe.copy()
    scored_dataframe["Correctness"] = correctness_scores
    scored_dataframe["Error Analysis"] = error_analysis
    return scored_dataframe


def ensure_manual_review_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    reviewed_dataframe = dataframe.copy()
    for column in MANUAL_REVIEW_COLUMNS:
        if column not in reviewed_dataframe.columns:
            reviewed_dataframe[column] = ""
    return reviewed_dataframe


def score_excel_file(path: Path) -> Path:
    dataframe = pd.read_excel(path)
    scored_dataframe = score_dataframe(dataframe)
    scored_dataframe.to_excel(path, index=False)
    return path


def score_directory(path: Path) -> list[Path]:
    updated_files: list[Path] = []
    for excel_path in sorted(path.rglob("*.xlsx")):
        updated_files.append(score_excel_file(excel_path))
    return updated_files


def prepare_manual_review_file(path: Path) -> Path:
    dataframe = pd.read_excel(path)
    reviewed_dataframe = ensure_manual_review_columns(dataframe)
    reviewed_dataframe.to_excel(path, index=False)
    return path


def prepare_manual_review_directory(path: Path) -> list[Path]:
    updated_files: list[Path] = []
    for excel_path in sorted(path.rglob("*.xlsx")):
        updated_files.append(prepare_manual_review_file(excel_path))
    return updated_files

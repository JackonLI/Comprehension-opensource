from __future__ import annotations

from pathlib import Path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_base_prompt(repo_root: Path, prompt_name: str) -> str:
    prompt_path = repo_root / "prompts" / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file does not exist: {prompt_path}")
    return _read_text(prompt_path)


def load_prompt_with_snmt(repo_root: Path, prompt_name: str, snmt_name: str) -> str:
    base_prompt = load_base_prompt(repo_root, prompt_name)
    snmt_path = repo_root / "snmt" / snmt_name
    if not snmt_path.exists():
        raise FileNotFoundError(f"SNMT file does not exist: {snmt_path}")
    snmt_text = _read_text(snmt_path)
    return f"{base_prompt}{snmt_text}"


def load_snmt_slices(repo_root: Path, snmt_name: str, slice_size: int) -> list[str]:
    snmt_path = repo_root / "snmt" / snmt_name
    if not snmt_path.exists():
        raise FileNotFoundError(f"SNMT file does not exist: {snmt_path}")
    lines = snmt_path.read_text(encoding="utf-8").splitlines(keepends=True)
    return [
        "".join(lines[index : index + slice_size])
        for index in range(0, len(lines), slice_size)
    ]

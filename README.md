# Seraph

This repository releases the open-source artifact for `Seraph`, a system for LLM-assisted network intent processing. The current public release focuses on the `intent comprehension` module, including datasets, prompts, topology assets, evaluation scripts, and the expert review workflow used in our study. Code & data for `Conflict detection & resolution` and `Deployment optimization` will come soon.

## Current Release

The current release includes:

- `intent dataset/`: natural-language intents and expected IR annotations
- `network/`: synthetic network topologies and generation scripts
- `snmt/`: semantics-network mapping tables for each topology
- `prompts/`: prompt templates used in the reported experiments
- `src/seraph_intent_comprehension/`: implementation of the intent comprehension workflow
- `scripts/`: command-line entry points for evaluation, automatic checking, expert review preparation, and feedback

## Installation

Use Python 3.9 or above.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

## API Configuration

Seraph intent comprehension is designed to run with a standard OpenAI-compatible chat completion API.

Before running experiments, copy `.env.example` to `.env` or export the variables in your shell and fill in your own credentials:

```bash
export SERAPH_API_KEY="your_key_here"
export SERAPH_API_BASE_URL="https://your-openai-compatible-endpoint/v1"
```

Optional settings:

- `SERAPH_API_KEYS`: comma-separated API keys for key rotation
- `SERAPH_TIMEOUT_SECONDS`
- `SERAPH_MAX_RETRIES`
- `SERAPH_LOG_LEVEL`

No private or personal API credentials are included in this repository.

## Repository Layout

```text
repository-root/
├── intent dataset/
├── network/
├── prompts/
├── scripts/
├── snmt/
└── src/seraph_intent_comprehension/
```

The evaluation code automatically looks for datasets under `intent dataset/`, and also accepts `intent datasets/` or `dataset/` if users rename the folder locally.

## Running Intent Comprehension

List the built-in dataset mappings:

```bash
python scripts/run_eval.py --model gpt-4o --mode basic --list-datasets
```

Run one dataset with the basic prompt:

```bash
python scripts/run_eval.py \
  --model gpt-4o \
  --mode basic \
  --topology campus_net \
  --task intent \
  --experiment-name paper_basic
```

Run the iterative variant for the extreme topology:

```bash
python scripts/run_eval.py \
  --model gpt-4o \
  --mode iterative \
  --topology extreme \
  --task protect \
  --experiment-name paper_iterative
```

Run the baseline variant:

```bash
python scripts/run_eval.py \
  --model gpt-4o-mini \
  --mode baseline \
  --topology cloud_net \
  --task intent \
  --experiment-name baseline
```

Run all registered datasets in one command:

```bash
python scripts/run_eval.py \
  --model gpt-4o \
  --mode basic \
  --all-datasets \
  --experiment-name full_run
```

Run a prompt ablation by overriding the prompt file:

```bash
python scripts/run_eval.py \
  --model gpt-4o \
  --mode basic \
  --all-datasets \
  --prompt-file prompt_without_examples.txt \
  --experiment-name ablation_without_examples
```

Outputs are written to `outputs/<experiment>/<mode>/<model>/<topology>/`.

## Evaluation Protocol

The evaluation workflow for the intent comprehension module is:

1. Run the model and generate output Excel files under `outputs/`.
2. Run the automatic structural checker if desired.
3. Prepare files for expert review.
4. Ask domain experts to manually annotate the generated outputs.
5. Optionally run the expert feedback loop on incorrect cases.

### Automatic Structural Check

```bash
python scripts/score_results.py --target outputs
```

This command writes:

- `Correctness`
- `Error Analysis`

These columns are generated automatically by comparing the parsed IR structure against the expected IR. This check is useful for large-scale screening, but it does not replace expert judgment.

### Preparing Expert Review

```bash
python scripts/prepare_manual_review.py --target outputs
```

This command adds the following columns when they are missing:

- `Expert Correctness`
- `Expert Error Type`
- `Expert Notes`

Reviewers can then open the output Excel files and manually annotate the generated IRs.

### Expert Feedback Loop

After expert review, run the interactive feedback loop on a scored or manually reviewed output file:

```bash
python scripts/run_feedback.py \
  --model gpt-4o-mini \
  --topology cloud_net \
  --task intent \
  --result-file outputs/baseline/baseline/gpt-4o-mini/cloud_net/intent_cloud_results.xlsx \
  --feedback-prompt-mode baseline
```

The feedback script:

- prefers `Expert Correctness` when manual annotations are available
- falls back to `Correctness` if expert annotations are not present
- records each session in a separate `*_feedback.xlsx` file
- keeps the original evaluation output unchanged

## Notice

### Release Plan

- `Conflict detection & resolution`: code and data coming soon.
- `Deployment optimization`: code and data coming soon.

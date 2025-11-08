# SAILED: Evaluation module

## Overview

Welcome to the **Evaluation** module! The module's purpose is to evaluate ATLAS and understand if it provides any learning benefits. There are three parts of the evaluation module:
- **Simulation**: Simulate tutoring sessions between ATLAS and learners, but also a Vanilla LLM tutor and learners. The course used for evaluation is always PYT101. (`simulation.py`)
- **Exam Prediction**: Using previously run and locally saved chat sessions (see `chat_sessions/`), predict a learner's exam results. More particularly, instead of asking the student agent to take the exam using newly acquired knowledge, we found that coherence in test results increased if we ask an external entity to predict what the student would answer. (`exam.py`)
- **Statistics**: With the saved exam results (see `exam_results/`), compute statistics to better understand the impact ATLAS has on personalised learning.

We built a CLI to play around with statistics, explained below.

## How to Use the Atlas Agent CLI

This CLI provides tools for running simulations, exams, and statistics calculations for the SAILED evaluation framework.

Run the CLI from the command line:

```sh
python src/evaluation/cli.py <mode> [options]
```

### Modes

- `simulation`: Run a tutoring simulation between a teacher and a learner agent.
- `exam`: Run an exam for one or all learners.
- `stats`: Calculate and display evaluation statistics.

### Options

- `-l`, `--learner-id`: Specify the learner ID (required for `simulation` and `exam` modes; use `"all"` only for `exam` mode).
- `-t`, `--tutoring-type`: Specify the tutoring agent type (`atlas` or `vanilla`, required for `simulation` mode).
- `-n`, `--max-chat-rounds`: Maximum number of chat rounds in the simulation (required for `simulation` mode).
- `-m`, `--llm`: LLM deployment name (default: `gpt-4.1`).

## Examples

**Run a simulation:**
```sh
python src/evaluation/cli.py simulation --learner-id learner_1 --tutoring-type atlas --max-chat-rounds 10
```

**Run an exam for a single learner:**
```sh
python src/evaluation/cli.py exam --learner-id learner_1
```

**Run exams for all learners:**
```sh
python src/evaluation/cli.py exam --learner-id all
```

**Calculate statistics:**
```sh
python src/evaluation/cli.py stats
```

## Notes

- All arguments are validated; missing required options will result in an error.
- The learner ID `learner_10` is reserved for demo purposes and cannot be used.
- For available learner IDs, check the `LEARNERS` dictionary in the codebase.
- The CLI uses Azure clients and may require appropriate credentials/configuration.

Some useful files:
- After running `simulation`, a transcript is saved in `chat_reports/`.
- After running `exam`, a report is saved in `exam_reports/`.
- After running `stats`, figures are available `figures/`.

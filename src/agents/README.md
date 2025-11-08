# ATLAS: Education Data module

## Overview

Welcome to the **Agents** module! The module includes all agent profiles used in the project:
- **ATLAS Agent**: The main agentic tutor profile and the heart of the system. It integrates with tools from the custom MCP, data persisted on Azure, and is tuned to guide students through a Course across sessions. (`atlas_agent.py`)
- **Vanilla Agent**: The vanilla LLM tutor profile used for evaluation. It has very minimal knowledge about the educational background during tutoring session (only the concept name!) and has minimal instructions to avoid altering its behaviour. (`vanilla_agent.py`)
- **Learner Agent**: The simulated learner profile used for evaluation, including tutoring simulations. The language model powering a learner agent may come from two providers:
    - Azure OpenAI (Semantic Kernel), with implementation at `sk_agent.py`
    - Ollama (for smaller models), with implementation at `ollama_agent.py`

## How to Use the Atlas Agent CLI

This CLI lets you interact with the Atlas conversational agent for a selected course and model, through the Terminal.

Run the CLI from the command line:

```sh
python src/agents/cli.py <course_id> [options]
```

### Arguments

- `<course_id>`: The ID of the course you want to use (required; see available IDs in `COURSES`).

### Options

- `-r`, `--reset-memory`: Reset memory data (progess, checkpoints) enabling cross-session continuity before starting.
- `-m`, `--llm`: Specify the LLM deployment name (default: `gpt-4.1`). Note that Ollama is not supported in this CLI, so only Foundry deployed models are accepted.

## Example

**Start a conversation with the Atlas agent for course `PYT101`:**
```sh
python src/agents/cli.py PYT101
```

**Start with memory reset:**
```sh
python src/agents/cli.py PYT101 --reset-memory
```

**Use a different LLM deployment:**
```sh
python src/agents/cli.py PYT101 --llm gpt-4.1-mini
```

## Conversation Loop

- Type your message and press Enter to interact with the agent.
- Type `exit` to end the session.

## Notes

- The CLI only uses the demo learner (`learner_10`), which is enrolled in all available courses.
- Azure credentials/configuration may be required.
- Available course IDs are defined in the `COURSES` dictionary.
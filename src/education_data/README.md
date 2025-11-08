# ATLAS: Education Data module

## Overview

Welcome to the **Education Data** module! The module's purpose is to easily manage the data needed to run ATLAS tutoring system. It heavily interacts with Azure Cosmos DB, Azure Blob Storage, and Azure AI Search to add, update, reset, and delete courses, learners, and the tutoring sessions between them.

We can find several submodules:
- `course/`:
    - Generate a syllabus (`syllabus.py`)
    - Decompose the syllabus into concepts (`roadmap.py`)
    - Generate an MCQ exam from a syllabus (`exam.py`)
    - Build a vector search index from the syllabus (`search_index.py`)
- `learner/`:
    - Add or update a Learner in Azure Cosmos DB. Learner data is stored in `data.py`.
    - Add or update its Concept Profile in Azure Cosmos DB. This object represents a learner's *background*, including it's prior knowledge level in each concept of a course. It is only for evaluation purposes (see **Evaluation** module!)
- `memory/` (memory architectures for cross-section continuity):
    - Create or reset a learner's progress in a particular course. This initialise all concept of the course to `not_started` for this learner, so ATLAS can start knowledge tracing from the beginning again.
    - Create or reset interaction checkpoints for a learner in a course. A checkpoint is a summary of a student-ATLAS interaction, used for continuity purposes across chat sessions.

You can modify content in `course/data.py` an `learner/data.py`, then use the CLI tools introduced below to persist the changes to Azure. Now, **how to use the CLI?**

## How to Use the Education Data CLI

This CLI allows you to interact with the `education_data` and perform the actions listed above.

Run the CLI from the command line:

```sh
uv run python3 src/education_data/cli.py <mode> [options]
```

### Modes

- `course`: Create course data, including syllabus, roadmap, exam, and search index (*update them if they exist*).
- `learner`: Create learner's profile, and init progress and checkpoints in enrolled courses (*update/reset if already exist*).
- `memory`: Init a learner's progress and checkpoint list for a particular course.
- `vector_index`: Rebuild the syllabus search index for a course.

### Options

- `-c`, `--course-id`: Specify the course ID (required for `course`, `memory`, and `vector_index` modes).
- `-l`, `--learner-id`: Specify the learner ID (required for `learner` and `memory` modes; use `"all"` to process all learners in `learner` mode).
- `-m`, `--llm`: Choose the LLM deployment name (default: `gpt-4.1-mini`).

## Examples

**Create a course:**
```sh
uv run python3 src/education_data/cli.py course --course-id PYT101
```

**Set up a learner:**
```sh
uv run python3 src/education_data/cli.py learner --learner-id learner_10
```
Or for all learners:
```sh
uv run python3 src/education_data/cli.py learner --learner-id all
```

**Reset ATLAS memory for a pair of student-course:**
```sh
uv run python3 src/education_data/cli.py memory --course-id PYT101 --learner-id learner_10
```

**Rebuild syllabus vector index:**
```sh
uv run python3 src/education_data/cli.py vector_index --course-id PYT101
```

## Notes

- All arguments are validated; missing required options will result in an error.
- The CLI uses Azure clients and may require appropriate credentials/configuration.
- For available course and learner IDs, check the `COURSES` and `LEARNERS` dictionaries in the codebase.
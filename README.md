![Alt text](images/atlas_background.jpg)

# ATLAS: Making Education More Personalised Through Agentic Tutoring

Welcome to ATLAS, an agentic Intelligent Tutoring System (ITS) guiding students throughout their enrolled university modules.

*This project has been developed on my university email address. This repo is a copy-paste of the final version.*

My Microsoft Tech Community article about ATLAS is available [here](https://techcommunity.microsoft.com/blog/educatordeveloperblog/atlas-your-ai-tutoring-agent-for-personalised-learning/4450466).

## Project Structure

Here are the main modules of my projects
- `src/education_data/` — Course and learner data management, workflows, and utilities.
- `src/agents/` — Conversational agents (Atlas, Vanilla, Learner).
- `src/evaluation/` — Simulation, exam, and statistics modules for evaluation.
- `src/model_context_protocol/` — Tool collection for ATLAS tutor agents.
- `src/utils/` — Shared utilities for Azure, logging, LLMs, and environment variables.

Other notable:
- `frontend/` - Chainlit frontned for testing ATLAS and better understand how it works in 

---

## Setup

### Environment

Clone the repository:
```sh
git clone https://github.com/danyhersco/atlas.git
cd irp-dh324
```

This project uses `uv`, an efficient package manager developed by Astral. If you don't have it installed already, follow those instructions:

- For Mac:

    ```sh
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

- For Windows

    ```sh
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    ```

Activate the `uv` Python environment and install dependencies from `pyproject.toml` and `uv.lock`.
```sh
uv sync
```

Install the package in editable mode:
```sh
uv pip install -e .
```

### Azure Resources

This project is tighlty linked to Microsoft Azure. It uses Cosmos DB, Blob Storage, and AI Search for data storing and indexing, Azure AI Foundry to deploy and manage LLMs, ACR and ACA to run simulations in the cloud, etc. For reproducibility, it is crucial that you have specific resources created and environment variables set up to be able to use the system.

#### 1. Create an Azure Subscription

If you do not already have an Azure subscription, [sign up here](https://azure.microsoft.com/en-us/free/).

#### 2. Set Up Azure AI Foundry

- Go to [Azure AI Foundry](https://ai.azure.com/) and create an AI Foundry profile (project, not hub-based!).
- Follow the [Getting Started with Azure AI Foundry](https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code?tabs=azure-ai-foundry&pivots=fdp-project) guide.

#### 3. Create Azure Cosmos DB Account

- In the Azure portal, create a new **Cosmos DB** account.
- Name the account **campus-connect**.
- Note the endpoint and key for your environment variables.

#### 4. Create Azure Blob Storage Containers

- Create a new **Storage Account**.
- Inside the account, create two containers:
  - `synthetic-data`, for storing syllabi and exams data *(the name is misleading and should be changed soon to `course-data`)*
  - `chat-reports`, for storing chat session reports

#### 5. Create Azure AI Search Service

- Create a new Azure AI Search service.
- Name the service **campus-connect**.
- Select the 'Basic' SKU, which costs around 75$ per month.
- Note the endpoint and admin key for your environment variables.

#### 6. Deploy Models on Foundry

- In Azure AI Foundry, deploy the models required for your application.
- Use deployment names as indicated in your `src/utils/llms.py` (e.g., `gpt-4.1`, `gpt-4.1-mini`).
- Ensure each deployment is accessible and the endpoint is noted.

#### 7. Fill All Required Environment Variables

Create a `.env` file in your project root and add the following variables indicated in `.env.example`, which is provided for you as a template.

Once these resources are created and configured, you will be able to run the system!

### Data Population

You can now populate Azure databases with course and learner data!

- For course data, run

    ```sh
    uv run python3 src/education_data/cli.py course -c all
    ```

- For learner data, run

    ```sh
    uv run python3 src/education_data/cli.py learner -l all
    ```

Note that alomst all courses (except the one for eval purposes, PYT101) are LLM-generated, then embedded. Those steps might take some time, around 1-2 minutes for each course.

## Frontend

Once you created your Azure subscription, deployed the resources, and populated the databases with education data, you can now open a local frontend app. It was developed using [`Chainlit`](https://docs.chainlit.io/get-started/overview), a framework for building chat-based web applications.

The command to open the app is:
```sh
cd frontend && uv run chainlit run --port 8000 app.py
```

If you land on the login page, enter username `dev` and password `atlas`.

The frontend opens a chat session between the dedicated demo learner (`learner_10`) and ATLAS. If you'd like to reset learner progress, run:

```sh
uv run python3 src/education_data/cli.py learner --learner-id learner_10
```

## CLI Modules

### Education Data CLI

Manage courses, learners, memory, and syllabus indexing.

- **Usage & options:**  See [`src/education_data/README.md`](src/education_data/how-to-use.md)

### Atlas Agent CLI

Interact with the Atlas conversational agent for a selected course.

- **Usage & options:**  See [`src/agents/README.md`](src/agents/how-to-use.md)

### Evaluation CLI

Run simulations, exams, and statistics calculations.

- **Usage & options:**  See [`src/evaluation/README.md`](src/evaluation/README.md)


## Testing

The project also includes unittests. To run them:

```sh
uv run pytest
```

*Note: They are exclusively for `education_data` and `utils` module.*


## Deliverables

My **project plan** and **final report** are available in `deliverables/` directory. Have a look, they have good content!

## License

This project is licensed under the [MIT License](LICENSE).

## Note

You might have noticed the `Dockerfile` with `.dockerignore`. Don't mind these. They are intended to create a containerised app to run simulations in Azure Container Apps, used for exam taking. They are full simulations going through the whole PYT101 course, so they are relatively costly and time-consuming. This is too overkill for examination, and not even needed to reproduce, because:
1. We can test simulation using the `simulation` CLI endpoint in `src/evaluation/cli.py`
2. Those long simulations used for exam taking have been downloaded and stored in `src/evaluation/chat_sessions/`

For any setup issue, please do not hesitate to contact me (dany.herscovitch24@imperial.ac.uk) :)
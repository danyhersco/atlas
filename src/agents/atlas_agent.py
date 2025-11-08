import os
import json
import asyncio
from uuid import uuid4
from pathlib import Path
from typing import AsyncGenerator
from datetime import datetime, timezone

from dotenv import load_dotenv
from semantic_kernel.connectors.mcp import MCPStdioPlugin
from semantic_kernel.contents import (
    ChatMessageContent,
    FunctionResultContent,
    FunctionCallContent,
)
from semantic_kernel.contents import ChatHistorySummarizationReducer
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (  # noqa: E501
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)


from education_data.learner.data import LEARNERS
from utils.clients import get_aoai_client, get_cosmos_client
from utils.logger_config import logger
from utils.azure_storage_utils import (
    get_cosmos_docs_with_fields,
    get_cosmos_docs_with_ids,
    upsert_cosmos,
)
from utils.llms import get_llm, LLMName
from utils.chat_completion import generate
from models.base import (
    CosmosContainer,
    Course,
    ChatSession,
)
from model_context_protocol.functions import (
    retrieve_concept_tool,
    update_concept_status_tool,
    retrieve_learner_progress_tool,
)


class AtlasAgent:
    def __init__(
        self,
        course: Course,
        learner_id: str,
        mcp_plugin: MCPStdioPlugin,
        model_name: str,
    ):
        # get llm object with key and endpoint
        self.llm = get_llm(name=LLMName(model_name))

        self.kernel = Kernel()  # init kernel
        self.agent = AzureChatCompletion(
            deployment_name=self.llm.name,
            api_key=self.llm.key,
            endpoint=self.llm.endpoint,
        )
        # add chat service and mcp plugin to kernel
        self.kernel.add_service(self.agent)
        self.kernel.add_plugin(  # for tool access
            mcp_plugin,
            plugin_name="mcp_server",
        )

        self.course = course
        self.learner_id = learner_id
        self.cosmos_client = get_cosmos_client()

        # init chat history (with chat summarisation)
        self.chat_history = self.create_chat_history(
            model_name="gpt-4.1-nano", target_count=7
        )
        # needed to enable llm-chosen function calls
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = (
            FunctionChoiceBehavior.Auto()
        )

        self.session_id = str(uuid4())
        self.create_chat_session_in_cosmos()
        self.aoai_client = get_aoai_client()

        # add concept id as dev message
        # (serves as delimiter between concept-focused chats)
        concept_id, _ = self.get_in_progress_concept()
        self.add_chat_round_in_cosmos(new_concept_id=concept_id)

    async def process_learner_message(
        self,
        message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Processes a learner's message and streams the Atlas agent's response.

        This method sends the learner's message to the agent, records
        tool/function calls, and yields response chunks as they are generated.
        It also adds chat round in chat session (Cosmos DB), manages concept
        switching, and triggers chat summarisation and checkpoint creation.

        Args:
            message (str): The learner's input message.

        Yields:
            str: Chunks of the assistant's response as they are generated.
        """
        logger.debug(f"Sending message to agent: {message[:20]}...")

        # recreate system message at each round to reflect live updates
        atlas_instructions_message = self.make_atlas_instructions_message()
        self.chat_history.messages.insert(0, atlas_instructions_message)
        self.chat_history.add_user_message(message)

        chunks = []
        tools = {}

        # stream ATLAS response
        async for chunk in self.agent.get_streaming_chat_message_content(
            chat_history=self.chat_history,
            settings=self.execution_settings,
            kernel=self.kernel,  # includes chat service and mcp tools
        ):
            if chunk is None:
                logger.warning("Received None chunk from streamed response.")
                continue

            # hacky way to keep track of tools called within the response
            # (had to dig deep inside SK's ChatMessageContent object)
            if chunk.role == AuthorRole.TOOL:
                for item in chunk.items:
                    if isinstance(item, FunctionResultContent):
                        tools[item.function_name] = item.metadata["arguments"]
                        break
                continue

            # solves problem of no written response when tool is called
            # (https://github.com/microsoft/semantic-kernel/issues/11451)
            if any(
                isinstance(item, (FunctionCallContent, FunctionResultContent))
                for item in chunk.items
            ):
                continue

            if chunk.content:
                chunks.append(chunk)
                yield chunk.content

        full_response = str(sum(chunks[1:], chunks[0]))
        logger.debug(f"Response from agent: {full_response[:20]}...")

        self.chat_history.add_assistant_message(full_response)
        self.chat_history.messages.pop(0)  # remove the system message

        # used to keep track of concept switching within chat session record
        new_concept_id = None
        if "switch_concept" in tools:
            new_concept_id = tools["switch_concept"]["next_concept_id"]
        self.add_chat_round_in_cosmos(
            user_message=message,
            assistant_message=full_response,
            new_concept_id=new_concept_id,
        )

        # summarise chat history and generate checkpoint, concurrently
        results = await asyncio.gather(
            self.chat_history.reduce(),
            self.add_checkpoint(
                user_message=message,
                assistant_message=full_response,
                model_name="gpt-4.1-nano",
            ),
        )
        is_reduced = results[0]  # check if chat summarisation occurred
        if is_reduced is not None:  # print first three messages for debug
            first_three_messages = "\n".join(
                f"- {m.role.value}: {m.content[:20]}"
                for m in self.chat_history.messages[:3]
            )
            logger.debug(
                f"Chat history reduced to {len(self.chat_history.messages)} "
                f"messages. First 3 messages:\n"
                f"{first_three_messages}"
            )

    def make_atlas_instructions_message(self) -> ChatMessageContent:
        """
        Constructs and returns the system prompt for the Atlas agent.

        This method loads the Atlas instructions template, gathers and formats
        relevant learner, course, concept, progress, and checkpoint data from
        Cosmos DB, and injects them into the prompt template. The resulting
        prompt is returned as a system message for use in the chat history.

        Returns:
            ChatMessageContent: Semantic Kernel's message object containing the
            formatted Atlas instructions and contextual data for the current
            learner and course.
        """

        # load prompt template
        atlas_instructions_file = (
            Path(__file__).resolve().parent / "instructions" / "atlas.txt"
        )
        with open(atlas_instructions_file, "r") as f:
            atlas_instructions = f.read().strip()

        # load learner data
        learner_doc = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.LEARNERS,
            document_ids=[self.learner_id],
        )[0]
        # load learner preferences data
        learning_preferences_data = learner_doc["learning_preferences"][
            self.course.id
        ]
        del learner_doc["course_ids"], learner_doc["learning_preferences"]
        learner_data = json.dumps(learner_doc, indent=4)

        # load course data
        course_doc = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.COURSES,
            document_ids=[self.course.id],
        )[0]
        del (
            course_doc["n_lectures"],
            course_doc["syllabus_url"],
            course_doc["exam_url"],
        )
        course_data = json.dumps(course_doc, indent=4)

        # concept needs to be called before progress (it update status!)
        _, concept_data = self.get_in_progress_concept()  # ignore concept_id

        # get progress data
        progress_data = retrieve_learner_progress_tool(
            learner_id=self.learner_id,
            course_id=self.course.id,
        )

        # get last 5 checkpoints
        checkpoints = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.CHECKPOINTS,
            document_ids=[f"checkpoints-{self.course.id}-{self.learner_id}"],
        )[0]
        checkpoints_data = "\n".join(checkpoints["checkpoints"][-5:])

        instructions = atlas_instructions.format(
            LEARNER_DATA=learner_data,
            LEARNING_PREFERENCES_DATA=learning_preferences_data,
            COURSE_DATA=course_data,
            PROGRESS_DATA=progress_data,
            CONCEPT_DATA=concept_data,
            CHECKPOINTS=checkpoints_data,
        )

        return ChatMessageContent(role=AuthorRole.SYSTEM, content=instructions)

    def get_in_progress_concept(self) -> tuple[str, str]:
        """
        Retrieves the current concept in progress for the learner
        in the course.

        This method queries Cosmos DB for concepts with status "in_progress"
        for the current learner and course:
        - If none are found, it retrieves the first concept, updates its
            status to "in_progress", and returns its ID and data.
        - If one is found, return ID and data directly
        - If multiple concepts are found in progress, an error is raised.

        Returns:
            tuple[str, str]: A tuple containing the concept ID and
                the concept data.

        Raises:
            ValueError: If multiple concepts are found in progress
        """

        # get all concepts in progress (though we expect only one)
        concepts_in_progress = get_cosmos_docs_with_fields(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.PROGRESSES,
            fields={
                "course_id": self.course.id,
                "learner_id": self.learner_id,
                "status": "in_progress",
            },
        )

        if len(concepts_in_progress) == 0:
            logger.info(
                "No concept is in progress, learner has probably not "
                "started the course yet. Retrieving the first concept."
            )
            first_concept = get_cosmos_docs_with_fields(
                cosmos_client=self.cosmos_client,
                container_name=CosmosContainer.PROGRESSES,
                fields={
                    "course_id": self.course.id,
                    "learner_id": self.learner_id,
                },
            )[0]
            concept_id = first_concept["concept_id"]  # first concept id
            logger.info(f"Using first concept: {concept_id}")

            # update first concept to in progress
            message = update_concept_status_tool(
                concept_id,
                status="in_progress",
                evidence="course start",
                learner_id=self.learner_id,
                course_id=self.course.id,
            )
            logger.info(message)

        elif len(concepts_in_progress) == 1:
            concept_id = concepts_in_progress[0]["concept_id"]
            logger.info(f"Using concept in progress: {concept_id}")
        else:  # >1 concept in progress is unexpected
            error_message = (
                "Expected 1 concept in progress, "
                f"but got {len(concepts_in_progress)}."
            )
            logger.error(error_message)
            raise ValueError(error_message)

        return concept_id, retrieve_concept_tool(concept_id)

    def add_chat_round_in_cosmos(
        self,
        user_message: str | None = None,
        assistant_message: str | None = None,
        new_concept_id: str | None = None,
    ) -> None:
        """
        Adds a chat round to the current chat session in Cosmos DB.

        This method appends the user's message, assistant's response,
        and a concept ID (as a delimiter between concept-focused chats)
        to the session's message history. It then writes to Cosmos DB

        Args:
            user_message (str | None): The learner's input message
                for this round.
            assistant_message (str | None): The assistant's response
                for this round.
            new_concept_id (str | None): The concept ID to add as a
                delimiter (if concept switched).

        Returns:
            None
        """
        # retrieve chat session, which includes list of messages
        session = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.CHAT_SESSIONS,
            document_ids=[str(self.session_id)],
        )[0]

        if user_message is not None:  # add user message
            session["messages"].append(
                {"role": "user", "content": user_message}
            )

        # add concept id as dev message if concept switching happened
        if new_concept_id is not None:
            session["messages"].append(
                {"role": "dev", "content": new_concept_id}
            )

        if assistant_message is not None:  # add assistant message
            session["messages"].append(
                {"role": "assistant", "content": assistant_message}
            )

        session["last_opened"] = datetime.now(timezone.utc).isoformat()

        # update chat session with new messages, in Cosmos DB
        database = self.cosmos_client.get_database_client("campus")
        container = database.get_container_client(
            CosmosContainer.CHAT_SESSIONS
        )
        container.replace_item(item=session["id"], body=session)

    async def add_checkpoint(
        self,
        user_message: str,
        assistant_message: str,
        model_name: str,
    ) -> None:
        """
        Generates and adds a checkpoint for the latest chat round in Cosmos DB.

        This method creates a checkpoint summary based on the current chat
        rounds, with extended context using the previous chat round, then
        appends the result to the learner's checkpoint history in Cosmos DB.

        Args:
            user_message (str): The learner's input message
                for the current round.
            assistant_message (str): The assistant's response
                for the current round.
            model_name (str): The LLM deployment name to use for checkpoint
                generation.

        Returns:
            None
        """
        logger.debug("Generating and adding checkpoint...")

        def get_previous_round(
            messages: list[ChatMessageContent],
        ) -> list[ChatMessageContent]:
            """Helper function to get the previous chat round messages."""
            filtered = [msg for msg in messages if msg.role != "system"]
            return filtered[max(0, len(filtered) - 4) : len(filtered) - 2]

        previous_round = get_previous_round(self.chat_history.messages)

        # get current and previous chat round
        current_round_str = (
            f"{AuthorRole.USER}: {user_message}\n"
            f"{AuthorRole.ASSISTANT}: {assistant_message}"
        )
        previous_round_str = "\n".join(
            f"{msg.role}: {msg.content}" for msg in previous_round
        )

        # read checkpoint system prompt template
        checkpoint_system_file = (
            Path(__file__).resolve().parent
            / "instructions"
            / "checkpoint_system.txt"
        )
        with open(checkpoint_system_file, "r") as f:
            checkpoint_system = f.read().strip()

        # read checkpoint user prompt template
        checkpoint_user_file = (
            Path(__file__).resolve().parent
            / "instructions"
            / "checkpoint_user.txt"
        )
        with open(checkpoint_user_file, "r") as f:
            checkpoint_user = f.read().strip()

        # format user prompt
        user_prompt = checkpoint_user.format(
            PREVIOUS_CHAT_ROUND=previous_round_str,
            CURRENT_CHAT_ROUND=current_round_str,
            LEARNER_NAME=LEARNERS[self.learner_id].name,
        )

        # generate checkpoint
        checkpoint = await generate(
            client=self.aoai_client,
            system_prompt=checkpoint_system,
            user_prompt=user_prompt,
            llm=model_name,
        )
        logger.info(f"Checkpoint generated: {checkpoint}")

        # add checkpoint to Cosmos DB
        checkpoints = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.CHECKPOINTS,
            document_ids=[f"checkpoints-{self.course.id}-{self.learner_id}"],
        )[0]
        checkpoints["checkpoints"].append(checkpoint)

        database = self.cosmos_client.get_database_client("campus")
        container = database.get_container_client(CosmosContainer.CHECKPOINTS)

        container.replace_item(item=checkpoints["id"], body=checkpoints)

    def create_chat_history(
        self, model_name: str, target_count: int
    ) -> ChatHistorySummarizationReducer:
        """
        Initializes and returns a chat history object with summarisation
        capabilities.

        This method loads the chat summary instructions template, sets up the
        chat service for the specified LLM deployment, and creates a
        ChatHistorySummarizationReducer to manage chat history and automatic
        summarisation when the message count exceeds the target.

        Args:
            model_name (str): The LLM deployment name to use for summarisation.
            target_count (int): The maximum number of messages before
                summarisation is triggered.

        Returns:
            ChatHistorySummarizationReducer: Semantic Kernel object to manage
                chat history and summarisation.
        """
        llm = get_llm(name=LLMName(model_name))

        # read chat summary instructions
        summary_instructions_file = (
            Path(__file__).resolve().parent
            / "instructions"
            / "chat_summary.txt"
        )
        with open(summary_instructions_file, "r") as f:
            summary_instructions = f.read().strip()

        return ChatHistorySummarizationReducer(
            target_count=target_count,
            service=AzureChatCompletion(  # init chat service
                deployment_name=llm.name,
                api_key=llm.key,
                endpoint=llm.endpoint,
            ),
            summarization_instructions=summary_instructions,
        )

    def create_chat_session_in_cosmos(self) -> None:
        """
        Simple wrapper to initiate a chat session
        and push it to Cosmos DB.
        """
        chat_session = ChatSession(
            id=self.session_id,
            course_id=self.course.id,
            learner_id=self.learner_id,
            atlas_model=self.llm.name,
            messages=[],
        )
        upsert_cosmos(
            cosmos_client=self.cosmos_client,
            documents=[chat_session.model_dump()],
            container_name=CosmosContainer.CHAT_SESSIONS,
        )

    @staticmethod
    async def mcp_connect() -> MCPStdioPlugin:
        """
        Initialises and connects the Model Context Protocol (MCP) server
        for Atlas.

        This method sets up MCPStdioPlugin with the appropriate directory,
        environment variables, and command-line arguments, then connects
        the plugin in STDIO communication mode for use with the Atlas agent.

        Returns:
            MCPStdioPlugin: The connected MCP plugin instance.
        """
        mcp_dir = (
            Path(__file__).resolve().parent.parent / "model_context_protocol"
        )
        load_dotenv()
        env_vars = dict(os.environ.copy())  # get env vars as dict

        logger.debug("Creating MCP Plugin...")
        mcp_plugin = MCPStdioPlugin(
            name="matlas",
            description=(
                "MCP for Matlas: an interface for a Learning Companion "
                "agent guiding students through a course."
            ),
            command="uv",
            args=[
                f"--directory={mcp_dir}",
                "run",
                "server.py",
            ],
            env=env_vars,  # add env vars in MCP server
        )
        await mcp_plugin.connect()
        return mcp_plugin

    @staticmethod
    async def mcp_disconnect(mcp_plugin: MCPStdioPlugin) -> None:
        if mcp_plugin is not None:
            await mcp_plugin.close()
        else:
            logger.warning("MCP Plugin is None, nothing to disconnect.")

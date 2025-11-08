from uuid import uuid4
from pathlib import Path
from datetime import datetime, timezone

from semantic_kernel.contents import ChatHistory
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (  # noqa: E501
    AzureChatPromptExecutionSettings,
)

from agents.learner_agent import LearnerAgent
from model_context_protocol.functions import update_concept_status_tool
from utils.clients import get_cosmos_client
from utils.logger_config import logger
from utils.azure_storage_utils import (
    get_cosmos_docs_with_ids,
    upsert_cosmos,
)
from utils.llms import get_llm, LLMName
from models.base import (
    CosmosContainer,
    Course,
    ChatSession,
)


class VanillaAgent:
    def __init__(
        self,
        course: Course,
        learner_id: str,
        model_name: str,
    ):
        self.course = course
        self.learner_id = learner_id
        self.cosmos_client = get_cosmos_client()

        # get concept IDs from the course
        self.concept_ids_list = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.ROADMAPS,
            document_ids=[f"rm-{course.id.value}"],
        )[0]["concept_ids"]

        # get llm object, including key and endpoint
        self.llm = get_llm(name=LLMName(model_name))

        self.kernel = Kernel()  # init the kernel
        self.agent = AzureChatCompletion(
            deployment_name=self.llm.name,
            api_key=self.llm.key,
            endpoint=self.llm.endpoint,
        )
        self.kernel.add_service(self.agent)  # add chat service to kernel

        # read and store system prompt template for vanilla agent
        vanilla_instructions_file = (
            Path(__file__).resolve().parent / "instructions" / "vanilla.txt"
        )
        with open(vanilla_instructions_file, "r") as f:
            self.vanilla_instructions = f.read().strip()

        self.session_id = str(uuid4())  # unique session id for Cosmos DB
        chat_session = ChatSession(  # init chat session
            id=self.session_id,
            course_id=self.course.id,
            learner_id=self.learner_id,
            atlas_model=self.llm.name,
            messages=[],
        )
        upsert_cosmos(  # upload empty chat session to Cosmos DB
            cosmos_client=self.cosmos_client,
            documents=[chat_session.model_dump()],
            container_name=CosmosContainer.CHAT_SESSIONS,
        )

    async def teach_concept(
        self,
        learner_agent: LearnerAgent,
        concept_id: str,
        chat_rounds: int = 12,
        verbose: bool = True,
    ) -> None:
        """
        Simulates a tutoring session between the vanilla tutor and a
        learner agent for a specific concept.

        The method alternates messages between the assistant (VanillaAgent)
        and the student (LearnerAgent) for a specified number of rounds.
        Each round, the assistant generates a response and the student replies.
        The conversation is stored in Cosmos DB, and the concept status is
        updated before and after the session.

        Args:
            learner_agent (LearnerAgent): The learner agent to interact with.
            concept_id (str): The ID of the concept to teach.
            chat_rounds (int, optional): Number of chat rounds to simulate.
                Defaults to 12.
            verbose (bool, optional): If True, prints assistant and learner
                responses to stdout. Defaults to True.

        Raises:
            ValueError: If the assistant returns no content in a chat round.
        """
        logger.debug(
            f"Teaching concept {concept_id} to learner {self.learner_id}"
        )

        # Update concept to "in progress"
        message = update_concept_status_tool(
            concept_id,
            status="in_progress",
            evidence="",
            learner_id=self.learner_id,
            course_id=self.course.id,
        )
        logger.info(message)

        # Get the concept information
        concept_data = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.CONCEPTS,
            document_ids=[concept_id],
        )[0]
        concept_data_str = (
            f"Title: {concept_data['title']}\n"
            f"Description: {concept_data['description']}\n"
            f"Goal: {concept_data['goal']}\n"
        )

        # format vanilla instruction with concept data
        instructions_formatted = self.vanilla_instructions.format(
            CONCEPT_DATA=concept_data_str
        )
        # init SK's chat history
        chat_history = ChatHistory(system_message=instructions_formatted)

        current_input = "Hello!"  # initial message
        chat_history.add_user_message(current_input)

        for i in range(chat_rounds):
            logger.info(
                f"Chat round {i + 1}/{chat_rounds} for concept {concept_id}"
            )

            # generate tutor message
            vanilla_response = await self.agent.get_chat_message_content(
                chat_history=chat_history,
                settings=AzureChatPromptExecutionSettings(),
            )
            if vanilla_response is None:
                error_message = "No content returned from Vanilla LLM."
                logger.error(error_message)
                raise ValueError(error_message)

            if verbose:
                print(
                    f"\n\nAssistant response:\n\n{vanilla_response.content}\n"
                )

            # generate learner message (from LearnerAgent class)
            learner_response = await learner_agent.process_message(
                vanilla_response.content
            )

            if verbose:
                print(f"\n\nLearner response:\n\n{learner_response}\n")

            # update chat history with new chat round
            chat_history.add_assistant_message(vanilla_response.content)
            chat_history.add_user_message(learner_response)

            # update current input for next round
            current_input = learner_response

        # add concept-focused chat history to Cosmos DB
        self.add_concept_chat_to_cosmos(chat_history, concept_id)

        # Update concept to "in progress"
        message = update_concept_status_tool(
            concept_id,
            status="mastered",  # might not be mastered, but does not matter
            evidence="",
            learner_id=self.learner_id,
            course_id=self.course.id,
        )
        logger.info(message)

    def add_concept_chat_to_cosmos(
        self, chat_history: ChatHistory, concept_id: str
    ) -> None:
        """
        Saves the concept-focused chat history to Cosmos DB
        for the current session.

        This method retrieves the chat session from Cosmos DB
        using the session ID, appends the concept ID as dev message
        and all chat messages (excluding the system prompt) to the
        session, and replaces the session document in the database.

        Args:
            chat_history (ChatHistory): The chat history object containing
                all tutoring messages for the concept.
            concept_id (str): The ID of the concept being taught.

        Returns:
            None
        """

        # retrieve the chat session from Cosmos DB
        chat_session = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.CHAT_SESSIONS,
            document_ids=[self.session_id],
        )[0]

        # concept id message (serves as delimiter between concept chats)
        messages = [{"role": "dev", "content": concept_id}]

        for message in chat_history.messages[1:]:  # Skip the system message
            messages.append({"role": message.role, "content": message.content})

        chat_session["messages"].extend(messages)  # new messages to session
        chat_session["last_opened"] = datetime.now(timezone.utc).isoformat()

        # replace session document in Cosmos with new messages
        database = self.cosmos_client.get_database_client("campus")
        container = database.get_container_client(
            CosmosContainer.CHAT_SESSIONS
        )
        container.replace_item(item=chat_session["id"], body=chat_session)

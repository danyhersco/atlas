from enum import StrEnum
from pathlib import Path


from agents.vanilla_agent import VanillaAgent
from models.base import (
    BlobContainer,
    ConceptStatus,
    CosmosContainer,
    ChatSession,
    Course,
)
from agents.atlas_agent import AtlasAgent
from agents.learner_agent import (
    LearnerAgent,
    SKLearnerAgent,
    OllamaLearnerAgent,
)
from utils.clients import get_blob_service_client, get_cosmos_client
from utils.logger_config import logger
from utils.azure_storage_utils import (
    get_cosmos_docs_with_fields,
    get_cosmos_docs_with_ids,
    upload_blob,
)


class LearnerType(StrEnum):
    OLLAMA = "ollama"
    SK = "sk"


class TutoringType(StrEnum):
    NO_TUTORING = "no_tutoring"
    VANILLA = "vanilla"
    ATLAS = "atlas"


class SimulationRunner:
    def __init__(
        self,
        course: Course,
        learner_id: str,
        teacher_model: str,
        learner_model: str,
    ):
        self.course = course
        self.learner_id = learner_id
        self.teacher_model = teacher_model
        self.learner_model = learner_model

        self.cosmos_client = get_cosmos_client()
        self.blob_service_client = get_blob_service_client()
        self.n_concepts = len(
            get_cosmos_docs_with_fields(
                cosmos_client=self.cosmos_client,
                container_name=CosmosContainer.CONCEPTS,
                fields={"course_id": self.course.id},
            )
        )

    async def run_simulation(
        self,
        learner_type: LearnerType,
        tutoring_type: TutoringType,
        max_chat_rounds: int = 20,
        verbose: bool = True,
    ) -> None:
        """
        Runs a tutoring simulation between a teacher agent and a learner agent.

        Depending on the specified learner and tutoring types, this method
        initializes the appropriate learner and teacher agents, executes the
        simulation for each concept (Vanilla) or as a conversation loop
        (ATLAS), and generates a chat report at the end. The simulation
        continues until all concepts are mastered or the maximum number of
        chat rounds is reached.

        Args:
            learner_type (LearnerType): The type of learner agent
                to use (SK or Ollama).
            tutoring_type (TutoringType): The type of teacher agent to use
                (Atlas or Vanilla).
            max_chat_rounds (int, optional): Maximum number of chat rounds
                (Atlas only). Defaults to 20.
            verbose (bool, optional): If True, prints conversation details
                to stdout. Defaults to True.

        Raises:
            ValueError: If an unsupported learner or tutoring type is
                specified.
            NotImplementedError: If 'no_tutoring' mode is selected.

        Returns:
            None
        """

        # do not run simulation if the learner is not
        # supposed to receive tutoring
        if tutoring_type == TutoringType.NO_TUTORING:
            raise NotImplementedError("No training mode is not supported.")

        if learner_type == LearnerType.OLLAMA:
            student = OllamaLearnerAgent(
                self.course, self.learner_id, model_name=self.learner_model
            )
        elif learner_type == LearnerType.SK:
            student = SKLearnerAgent(
                self.course, self.learner_id, model_name=self.learner_model
            )
        else:
            raise ValueError(f"Unsupported simulation mode: {learner_type}")

        if tutoring_type == TutoringType.ATLAS:
            mcp_plugin = await AtlasAgent.mcp_connect()
            teacher = AtlasAgent(
                self.course, self.learner_id, mcp_plugin, self.teacher_model
            )
            await self.run_atlas_simulation(
                teacher, student, max_chat_rounds, verbose
            )
            await AtlasAgent.mcp_disconnect(mcp_plugin)

        elif tutoring_type == TutoringType.VANILLA:
            teacher = VanillaAgent(
                course=self.course,
                learner_id=self.learner_id,
                model_name=self.teacher_model,
            )
            # in vanilla mode, we teach concepts one by one
            # after the other, with 12 chat rounds per concept by default
            for concept_id in teacher.concept_ids_list:
                await teacher.teach_concept(
                    student, concept_id, verbose=verbose
                )

        # retrieve newly created chat session from cosmos
        chat_session = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.CHAT_SESSIONS,
            document_ids=[teacher.session_id],
        )[0]
        chat_session = ChatSession(**chat_session)

        # export markdown report of tutoring session
        self._make_save_and_upload_chat_report(
            chat_session, teacher.session_id
        )

    async def run_atlas_simulation(
        self,
        teacher: AtlasAgent,
        student: LearnerAgent,
        max_chat_rounds: int,
        verbose: bool = True,
    ) -> None:
        """
        Runs an ATLAS tutoring simulation between a teacher agent
        and a learner agent.

        This method initiates a conversation loop for a specified number
        of chat rounds. In each round, the teacher agent (ATLAS) generates
        a response to the learner's input, and the learner agent replies.
        The loop continues until all concepts are mastered or the maximum
        number of chat rounds is reached. Optionally, prints conversation
        details to stdout.

        Args:
            teacher (AtlasAgent): The Atlas teacher agent.
            student (LearnerAgent): The learner agent.
            max_chat_rounds (int): Maximum number of chat rounds to run.
            verbose (bool, optional): If True, prints conversation details
                to stdout. Defaults to True.

        Returns:
            None
        """
        logger.debug("Starting conversation...")

        current_input = "Hello!"

        for i in range(max_chat_rounds):
            # exit conversation loop if all concepts are mastered
            if self._are_all_concepts_mastered():
                logger.info("All concepts mastered! End of Tutoring!")
                break

            logger.info(f"\nRound {i + 1} of conversation:\n")

            # stream ATLAS response
            chunks = []
            if verbose:
                print("\nAssistant:\n")
            async for chunk in teacher.process_learner_message(current_input):
                if verbose:
                    print(chunk, end="")
                chunks.append(chunk)

            atlas_response = "".join(chunks)  # get full response

            # generate student reponse
            student_response = await student.process_message(atlas_response)

            if verbose:
                print(f"\n\nStudent response:\n\n{student_response}\n")

            # update current input for next round
            current_input = student_response

    def _are_all_concepts_mastered(self):
        """
        Retrieves the number of mastered concepts for the learner's
        progress and returns True if it matches the total number of
        concepts (else False)
        """
        n_mastered = len(
            get_cosmos_docs_with_fields(
                cosmos_client=self.cosmos_client,
                container_name=CosmosContainer.PROGRESSES,
                fields={
                    "learner_id": self.learner_id,
                    "course_id": self.course.id,
                    "status": ConceptStatus.MASTERED.value,
                },
            )
        )

        if n_mastered == self.n_concepts:
            return True
        return False

    def _make_save_and_upload_chat_report(
        self, chat_session: ChatSession, session_id: str
    ) -> None:
        """
        Creates a markdown report for the chat session, saves it locally,
        and uploads it to Azure Blob Storage.

        This method formats the chat session messages into a readable markdown
        file, including course, learner, teacher model, learner model, and
        session details. Each message is labeled by role (student, teacher,
        or dev). The report is saved locally and then uploaded to the
        designated blob container.

        Args:
            chat_session (ChatSession): The chat session object containing
                all messages.
            session_id (str): The unique identifier for the chat session.

        Returns:
            None
        """
        logger.debug(f"Creating chat report for session: {session_id}")
        # nicely formatted role mapping
        role_map = {
            "user": "👩‍🎓 Student",
            "assistant": "👨‍🏫 Teacher",
            "dev": "🛠️ Dev",
        }

        # initiate first lines giving practical info about the session
        lines = [
            "# Conversation Report",
            f"Course: {chat_session.course_id}\n",
            f"Learner: {chat_session.learner_id}\n",
            f"Teacher model: {self.teacher_model}\n",
            f"Learner model: {self.learner_model}\n",
            f"Session ID: {session_id}\n",
            "## Messages\n",
        ]

        # append messages to the report
        for msg in chat_session.messages:
            if not msg.content:
                continue
            speaker = role_map[msg.role]
            lines.append(f"**{speaker}:**\n\n{msg.content}\n")

        markdown_output = "\n".join(lines)

        # save report to chat_reports directory
        dirpath = Path(__file__).resolve().parent / "chat_reports"
        dirpath.mkdir(parents=True, exist_ok=True)
        filepath = dirpath / f"{session_id}.md"

        with open(filepath, "w") as f:
            f.write(markdown_output)

        # upload report to Azure Blob Storage
        upload_blob(
            blob_service_client=self.blob_service_client,
            local_filepath=str(filepath),
            container_name=BlobContainer.CHAT_REPORTS,
            base_filename=f"{session_id}.md",
        )

        logger.info(
            f"Chat report created at: {dirpath}/{session_id}.md "
            "and successfully uploaded to Azure Blob Storage"
        )

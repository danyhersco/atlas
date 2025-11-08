from pathlib import Path
from abc import ABC, abstractmethod


from models.base import ConceptProfile, CosmosContainer, Course
from utils.azure_storage_utils import (
    get_cosmos_docs_with_fields,
    get_cosmos_docs_with_ids,
)
from utils.clients import get_cosmos_client
from utils.logger_config import logger


class LearnerAgent(ABC):
    """
    Abstract base class for learner agents.
    """

    def __init__(self, course: Course, learner_id: str, model_name: str):
        self.course = course
        self.learner_id = learner_id
        self.model_name = model_name
        self.cosmos_client = get_cosmos_client()

        # read concept profile
        self.concept_profile = ConceptProfile(
            **get_cosmos_docs_with_ids(
                cosmos_client=self.cosmos_client,
                container_name=CosmosContainer.CONCEPT_PROFILES,
                document_ids=[f"cp-{self.learner_id}"],
            )[0]
        )

    @abstractmethod
    async def process_message(self, message: str, trunc: int = 7) -> str:
        """
        Abstract method to process a learner's message and return a response.

        Implementations should simulate the learner's reply to a given tutoring
        message, optionally truncating the context to a specified number of
        previous messages if that number is exceeded.

        Args:
            message (str): The tutor message to process.
            trunc (int, optional): The number of previous messages to
                include in context. Defaults to 7.

        Returns:
            str: The learner agent's response to the tutor message.
        """
        pass

    def make_instructions(self) -> str:
        # read learner system prompt templat
        learner_instructions_file = (
            Path(__file__).resolve().parent.parent
            / "instructions"
            / "learner.txt"
        )
        with open(learner_instructions_file, "r") as f:
            learner_instructions = f.read().strip()

        # get learner name
        learner_name = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.LEARNERS,
            document_ids=[self.learner_id],
        )[0]["name"]

        # get course name
        course_name = get_cosmos_docs_with_ids(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.COURSES,
            document_ids=[self.course.id],
        )[0]["name"]

        # get learner's prior level in the concept being taught,
        # to alter their behaviour accordingly
        concept_id, knowledge_status = (
            self.get_in_progress_concept_knowledge_status()
        )
        logger.warning(
            f"Knowledge status for {concept_id} is {knowledge_status}"
        )

        return learner_instructions.format(
            LEARNER_NAME=learner_name,
            COURSE_NAME=course_name,
            CONCEPT_ID=concept_id,
            KNOWLEDGE_STATUS=knowledge_status,
        )

    def get_in_progress_concept_knowledge_status(self) -> tuple[str, str]:
        """
        Retrieves the current concept being taught, as well the learner's
        knowledge status in that concept, prior to course start.

        Returns:
            tuple[str, str]: A tuple containing the concept ID and the
                learner's knowledge status.

        Raises:
            ValueError: If zero or more than one concept is in progress,
                or if the concept's prior level is unknown.
        """

        def find_knowledge_status(concept_id: str) -> str:
            """Helper function navigating concept_profile to
            get the knowledge status given a concept_id"""
            if concept_id in self.concept_profile.not_started:
                return "not_started"
            elif concept_id in self.concept_profile.confused:
                return "confused"
            elif concept_id in self.concept_profile.mastered:
                return "mastered"
            raise ValueError(f"Unknown prior level for concept {concept_id}")

        # get concept in progress
        concepts_in_progress = get_cosmos_docs_with_fields(
            cosmos_client=self.cosmos_client,
            container_name=CosmosContainer.PROGRESSES,
            fields={
                "course_id": self.course.id,
                "learner_id": self.learner_id,
                "status": "in_progress",
            },
        )

        # there should be one concept in progress
        if not concepts_in_progress or len(concepts_in_progress) > 1:
            raise ValueError("Zero or 2+ concepts are not being treated.")

        concept_id = concepts_in_progress[0]["concept_id"]
        knowledge_level = find_knowledge_status(concept_id)

        return concept_id, knowledge_level

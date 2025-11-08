from azure.cosmos import CosmosClient

from utils.logger_config import logger
from utils.azure_storage_utils import upsert_cosmos
from models.base import CheckpointList, CosmosContainer, CourseID


def reset_checkpoints_in_cosmos(
    learner_id: str,
    course_id: CourseID,
    cosmos_client: CosmosClient,
) -> None:
    """
    Resets the interaction checkpoints of a learner in a specific course.
    A checkpoint is an LLM-generated summary of a chat round (student-
    tutor pair of messages). It serves as a long-term memory architecture
    for ATLAS to pick up where it left off in the last session. Checkpoints
    are stored in Cosmos DB in `checkpoints` container. Each pair of
    learner-course has a unique document.

    If no checkpoint entry exists, it sets up a document in Cosmos DB
    """
    logger.debug(
        "Resetting/creating checkpoint list in Cosmos DB for learner "
        f"{learner_id} in course {course_id}..."
    )
    # structure of document in `checkpoints` container
    checkpoint_list = CheckpointList(
        id=f"checkpoints-{course_id}-{learner_id}",
        course_id=course_id,
        learner_id=learner_id,
        checkpoints=[],
    )
    # upload it to Cosmos DB
    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=[checkpoint_list.model_dump(mode="json")],
        container_name=CosmosContainer.CHECKPOINTS,
    )
    logger.info(
        f"Checkpoint list for learner {learner_id} "
        f"in course {course_id} uploaded successfully."
    )

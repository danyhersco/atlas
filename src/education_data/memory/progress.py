from azure.cosmos import CosmosClient

from models.base import (
    CosmosContainer,
    CourseID,
    LearnerProgress,
    ConceptStatus,
)
from utils.azure_storage_utils import (
    upsert_cosmos,
    delete_cosmos_with_fields,
    get_cosmos_docs_with_ids,
)
from utils.logger_config import logger


def reset_progress_in_cosmos(
    learner_id: str,
    course_id: CourseID,
    cosmos_client: CosmosClient,
) -> None:
    """
    Resets the progress of a learner in a specific course.
    In Cosmos DB, a progress entry has learner_id, course_id,
    concept_id and status (mastered, confused, not_started, in_progress).
    This functions resets all concept status of the learner in the course
    to 'not_started'.

    If no progress entry exists, it creates them.
    """
    logger.debug(
        f"Resetting/creating progress in Cosmos DB for learner {learner_id}..."
    )

    # get the list of concept ids from the course roadmap
    concept_ids = get_cosmos_docs_with_ids(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.ROADMAPS,
        document_ids=[f"rm-{course_id}"],
    )[0]["concept_ids"]

    learner_progress = []

    for concept_id in concept_ids:
        learner_progress.append(
            # structure of a progress entry in
            # `progresses` Cosmos container
            LearnerProgress(
                id=f"{learner_id}-{concept_id}",
                course_id=course_id,
                concept_id=concept_id,
                learner_id=learner_id,
                status=ConceptStatus.NOT_STARTED,
            )
        )

    logger.info(
        f"Progress for learner {learner_id} initialised "
        f"with {len(learner_progress)} concepts."
    )

    # delete existing progress entries in Cosmos DB if exist
    delete_cosmos_with_fields(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.PROGRESSES,
        fields={"course_id": course_id, "learner_id": learner_id},
    )
    # re-upload the new initialised progress entries
    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=[
            progress.model_dump(mode="json") for progress in learner_progress
        ],
        container_name=CosmosContainer.PROGRESSES,
    )

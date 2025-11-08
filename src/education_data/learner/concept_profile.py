import random

from azure.cosmos import CosmosClient

from models.base import (
    ConceptProfile,
    CosmosContainer,
    Learner,
    LearnerLevel,
)
from utils.logger_config import logger
from utils.azure_storage_utils import upsert_cosmos, get_cosmos_docs_with_ids


def reset_concept_profile_in_cosmos(
    cosmos_client: CosmosClient, learner: Learner
) -> None:
    """
    [Only for evaluation purposes!] Creates a synthetic learner background
    by randomising concept allocation into mastery, confusion, and not_started
    buckets. This concept profile is not visible to ATLAS, but only the
    learner. It represents their status of understanding for each concept
    prior to enrolling in the course.

    Note: As evaluation learners are only enrolled in PYT101, this function
    is only applied to that course. We still do not hardcode it to provide
    flexibility in future work.
    """
    logger.debug(f"Creating concept profiles for learner {learner.id}...")

    if len(learner.course_ids) > 1:  # Ignore demo learner (learner_10)
        logger.warning(
            "Eval learners are only enrolled in one course only (PYT101). "
            f"{learner.id} is enrolled in multiple courses."
        )
        return

    course_id = learner.course_ids[0]  # only one course for eval learners
    # retrieve the list of concepts from the roadmap of the course
    concept_ids = get_cosmos_docs_with_ids(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.ROADMAPS,
        document_ids=[f"rm-{course_id}"],
    )[0]["concept_ids"]

    buckets = {"not_started": [], "confused": [], "mastered": []}
    n = len(concept_ids)

    # shuffle to randomise distribution
    shuffled = concept_ids.copy()
    random.shuffle(shuffled)

    if learner.level == LearnerLevel.BEGINNER:
        # 10% mastered, 50% confused, 40% not started
        mastered_count = int(0.1 * n)
        confused_count = int(0.5 * n)
        buckets["mastered"] = shuffled[:mastered_count]
        buckets["confused"] = shuffled[
            mastered_count : mastered_count + confused_count
        ]
        buckets["not_started"] = shuffled[mastered_count + confused_count :]

    elif learner.level == LearnerLevel.INTERMEDIATE:
        # 30% mastered, 30% confused, 40% not started
        mastered_count = int(0.3 * n)
        confused_count = int(0.3 * n)
        buckets["mastered"] = shuffled[:mastered_count]
        buckets["confused"] = shuffled[
            mastered_count : mastered_count + confused_count
        ]
        buckets["not_started"] = shuffled[mastered_count + confused_count :]

    elif learner.level == LearnerLevel.ADVANCED:
        # 50% mastered, 10% confused, 40% not started
        mastered_count = int(0.5 * n)
        confused_count = int(0.1 * n)
        buckets["mastered"] = shuffled[:mastered_count]
        buckets["confused"] = shuffled[
            mastered_count : mastered_count + confused_count
        ]
        buckets["not_started"] = shuffled[mastered_count + confused_count :]

    else:
        logger.warning(
            "Learner has no level. Skipping as they are not an eval learner"
        )
        return

    # build concept profile object, serving as the structure for Cosmos DB
    concept_profile = ConceptProfile(
        id=f"cp-{learner.id}",
        learner_id=learner.id,
        course_id=course_id,
        not_started=buckets["not_started"],
        confused=buckets["confused"],
        mastered=buckets["mastered"],
    )
    upsert_cosmos(  # upload object to Cosmos DB
        cosmos_client=cosmos_client,
        documents=[concept_profile.model_dump(mode="json")],
        container_name=CosmosContainer.CONCEPT_PROFILES,
    )

from pathlib import Path

from openai import AsyncAzureOpenAI
from azure.cosmos import CosmosClient
from azure.storage.blob import BlobServiceClient

from education_data.course.syllabus import (
    generate_syllabus,
)
from education_data.course.exam import generate_exam, save_and_upload_exam
from education_data.course.roadmap import (
    generate_roadmap,
    save_and_upload_roadmap,
)
from education_data.learner.concept_profile import (
    reset_concept_profile_in_cosmos,
)
from education_data.memory.progress import reset_progress_in_cosmos
from education_data.memory.checkpoint import reset_checkpoints_in_cosmos
from models.base import CosmosContainer, Course, CourseID, Learner
from education_data.course.data import COURSES
from education_data.course.syllabus import save_and_upload_syllabus
from education_data.course.search_index import make_syllabus_search_index
from education_data.learner.data import (
    LEARNERS,
    LEARNER_ID_TO_COURSE_ID,
)
from utils.logger_config import logger
from utils.llms import LLM

from utils.azure_storage_utils import upsert_cosmos


async def create_course(
    openai_client: AsyncAzureOpenAI,
    cosmos_client: CosmosClient,
    blob_client: BlobServiceClient,
    course: Course,
    llm: LLM,
) -> None:
    """
    Creates a university course. This function handles the course generation
    and ingestion, populating Azure Cosmos DB and Blob Storage. If the course
    already exists, it will be updated with the new content.

    This function generates a syllabus for any of the available courses
    in course/data.py. It then ingests the syllabus:
    - Course decomposition (Roadmap)
    - Build a vector index for RAG
    - Exam generation
    It then resets learner profiles for all those enrolled in the course,
    including progress data, interaction checkpoints, concept profiles.

    Note: Syllabus generation is skipped for PYT101 as it is a real course
    for ATLAS evaluation purposes. Only ingestion will occur.
    """

    logger.info("Starting course data generation...")

    if course.id != CourseID.PYT101:  # skip syllabus generation for PYT101
        syllabus = await generate_syllabus(
            client=openai_client,
            course=course,
            llm=llm,
        )
    else:  # load PYT101 syllabus directly as it is a real course
        logger.warning(
            "PYT101 course does not have a syllabus generation step, skipping."
        )
        filepath = (
            Path(__file__).resolve().parent
            / "course"
            / "syllabi"
            / "PYT101.md"
        )
        with open(filepath, "r") as file:
            syllabus = file.read()

    save_and_upload_syllabus(syllabus, course.id, blob_client)

    # chunk, embed, and load in Azure AI Search
    make_syllabus_search_index(
        syllabus=syllabus,
        index_name=course.id.lower(),
    )

    # perform course decomposition into a concept roadmap
    roadmap = await generate_roadmap(
        openai_client=openai_client, course=course, llm=llm
    )
    save_and_upload_roadmap(
        cosmos_client=cosmos_client,
        course_roadmap=roadmap,
    )

    # generate exam with one question per concept in the roadmap
    exam = await generate_exam(openai_client, cosmos_client, course, llm)
    save_and_upload_exam(exam, course.id, blob_client)

    # upload course basic info in Azure Cosmos DB
    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=[course.model_dump(mode="json")],
        container_name=CosmosContainer.COURSES,
    )

    def find_enrolled_learners(course_id: CourseID) -> list[Learner]:
        """Find all learners enrolled in a specific course."""
        logger.debug(f"Finding enrolled learners for course {course_id}...")
        enrolled_learners = [
            learner
            for learner in LEARNERS.values()
            if course_id in learner.course_ids
        ]
        logger.info(
            "Found "
            f"{', '.join(learner.name for learner in enrolled_learners)} "
            f"as learners of {course_id}."
        )
        return enrolled_learners

    enrolled_learners = find_enrolled_learners(course.id)
    for learner in enrolled_learners:
        logger.info(f"{learner.id} is enrolled in {course.id}.")
        upsert_cosmos(
            cosmos_client=cosmos_client,
            documents=[learner.model_dump(mode="json")],
            container_name=CosmosContainer.LEARNERS,
        )
        reset_progress_in_cosmos(
            learner_id=learner.id,
            course_id=course.id,
            cosmos_client=cosmos_client,
        )

        if course.id == CourseID.PYT101:
            logger.info("PYT101 is for eval. Generating concept profile...")
            reset_concept_profile_in_cosmos(
                cosmos_client=cosmos_client,
                learner=learner,
            )

        reset_checkpoints_in_cosmos(
            learner_id=learner.id,
            course_id=course.id,
            cosmos_client=cosmos_client,
        )


def create_learner(
    cosmos_client: CosmosClient,
    learner: Learner,
) -> None:
    """
    Creates a learner. This function populates Azure Cosmos DB
    with learner data including progress, concept profile,
    and interaction checkpoints. If the learner already exists
    in the database it will be reinitialised.
    """

    logger.info("Starting learner data generation...")

    # upload learner basic info to Azure Cosmos DB
    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=[learner.model_dump(mode="json")],
        container_name=CosmosContainer.LEARNERS,
    )
    for course_id in learner.course_ids:
        course = COURSES[course_id]  # get course info using id
        # reset progress by reinit all concept
        # status to 'not_started'
        reset_progress_in_cosmos(
            learner_id=learner.id,
            course_id=course.id,
            cosmos_client=cosmos_client,
        )
        # recreate a concept profile representing learner's
        # knowledge in each concept, prior to enrollement
        reset_concept_profile_in_cosmos(
            cosmos_client=cosmos_client,
            learner=learner,
        )
        # empty list of past interactions with ATLAS
        reset_checkpoints_in_cosmos(
            learner_id=learner.id,
            course_id=course.id,
            cosmos_client=cosmos_client,
        )


def reset_memory(
    cosmos_client: CosmosClient, learner_id: str, course_id: CourseID
) -> None:
    """
    Resets memory of a learner in a particular course. This function
    resets memory architectures used to maintain an across-session
    learning experience. This data includes learner progress and
    interaction checkpoints, which we reset in Azure Cosmos DB.
    """
    course = COURSES[course_id]  # get course info using id
    learner = LEARNERS[learner_id]  # get learner info using id
    if course.id not in LEARNER_ID_TO_COURSE_ID[learner.id]:
        logger.error(
            f"Learner {learner.id} is not enrolled in course {course.id}. "
            "Cannot re-initialise memory."
        )
        return
    logger.info(
        "Re-initialising learner progress for course "
        f"{course.id} and learner {learner.id}..."
    )
    # reset progress by reinit all concept
    # status to 'not_started'
    reset_progress_in_cosmos(
        learner_id=learner.id,
        course_id=course.id,
        cosmos_client=cosmos_client,
    )
    # empty list of past interactions with ATLAS
    reset_checkpoints_in_cosmos(
        learner_id=learner.id,
        course_id=course.id,
        cosmos_client=cosmos_client,
    )

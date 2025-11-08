import json
import os
import asyncio

from openai import AsyncAzureOpenAI
from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient

from model_context_protocol.functions import retrieve_concept_tool
from models.base import BlobContainer, CosmosContainer, Course, CourseID
from education_data.prompts import EXAM_SYSTEM_PROMPT, EXAM_USER_PROMPT
from utils.llms import LLM
from utils.chat_completion import generate
from utils.logger_config import logger
from utils.azure_storage_utils import upload_blob, get_cosmos_docs_with_ids
from models.base import ExamQuestion


def save_and_upload_exam(
    exam: list[ExamQuestion],
    course_id: CourseID,
    blob_service_client: BlobServiceClient,
) -> None:
    """
    Saves exam locally as JSON and uploads the file in Azure Blob Storage.
    """
    script_path = os.path.dirname(os.path.abspath(__file__))
    dirpath = os.path.join(script_path, "exams")
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, f"{course_id}.json")

    logger.info(f"Saving exam at {filepath}...")

    # convert list[ExamQuestion] to JSON and write to filepath
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(
            [q.model_dump() for q in exam], f, indent=4, ensure_ascii=False
        )

    logger.info(f"Exam succefully saved at {filepath}.")

    # Upload newly created json file to Azure Blob Storage
    upload_blob(
        blob_service_client=blob_service_client,
        local_filepath=filepath,
        container_name=BlobContainer.SYNTHETIC_DATA,
        base_filename=f"exam_{course_id}.json",
    )


async def generate_exam(
    openai_client: AsyncAzureOpenAI,
    cosmos_client: CosmosClient,
    course: Course,
    llm: LLM,
) -> list[ExamQuestion]:
    """
    Generates an exam for the given course.

    This function achieves this by generating one question per
    concept in the course roadmap.
    """

    async def generate_question(
        concept_id: str,
    ) -> ExamQuestion:
        """
        Generates a single multiple-choice exam question
        testing the given concept. This logic is wrapped in a function
        to enable concurrent questions generation.
        """
        logger.debug(f"Generating exam questions for concept {concept_id}...")

        # retrieves the concept, including learnable content
        # and exercises. asyncio.to_thread makes this call non-blocking
        concept_formatted = await asyncio.to_thread(
            retrieve_concept_tool, concept_id
        )
        user_prompt = EXAM_USER_PROMPT.format(
            CONCEPT_ID=concept_id,
            COURSE_NAME=course.name,
            SECTION_CONTENT=concept_formatted,
        )
        # structured output to ensure we get both question and choices
        section_question = await generate(
            client=openai_client,
            system_prompt=EXAM_SYSTEM_PROMPT,  # no placeholder
            user_prompt=user_prompt,
            llm=llm.name,
            output_format=ExamQuestion,
        )
        logger.info(f"Generated a question for concept {concept_id}.")
        return section_question  # type: ignore

    logger.debug(f"Generating exam for course {course.id}...")

    # retrieve all concept ids from course
    concept_ids = get_cosmos_docs_with_ids(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.ROADMAPS,
        document_ids=[f"rm-{course.id}"],
    )[0]["concept_ids"]

    # initiate the tasks
    question_tasks = [
        generate_question(concept_id) for concept_id in concept_ids
    ]

    exam = await asyncio.gather(*question_tasks)  # run concurrently
    for question in exam:  # prepend choices with letters
        question.choices = [
            f"{letter}. {choice}"
            for letter, choice in zip("ABCDE", question.choices)
        ]

    logger.info(
        f"Exam for course {course.id} succefully generated, "
        f"with {len(exam)} questions."
    )

    return exam

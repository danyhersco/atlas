import os
import re
import asyncio
import shutil
from pathlib import Path

from pydantic import BaseModel
from openai import AsyncAzureOpenAI
from azure.storage.blob import BlobServiceClient

from education_data.course.search_index import chunk_syllabus
from models.base import (
    BlobContainer,
    Course,
    CourseID,
    LectureOutline,
    Section,
)
from education_data.prompts import (
    COURSE_OUTLINE_SYSTEM_PROMPT,
    COURSE_OUTLINE_USER_PROMPT,
    LECTURE_SYSTEM_PROMPT,
    LECTURE_USER_PROMPT,
)
from utils.chat_completion import generate
from utils.logger_config import logger
from utils.llms import LLM
from utils.azure_storage_utils import upload_blob


def save_and_upload_syllabus(
    syllabus_text: str,
    course_id: CourseID,
    blob_service_client: BlobServiceClient,
) -> None:
    """
    Populates Azure Blob Storage with the syllabus, and
    saves it locally.

    This function uploads:
    - Saves locally and uploads the whole syllabus
        in `synthetic-data` container
    - Saves locally and uploads each section of the
        syllabus in `synthetic-data` container

    """
    # create syllabi directory, save syllabus in md format
    dirpath = Path(__file__).resolve().parent / "syllabi"
    os.makedirs(dirpath, exist_ok=True)
    md_filepath = dirpath / f"{course_id}.md"
    with open(md_filepath, "w") as f:
        f.write(syllabus_text)

    logger.info(f"Successfully saved syllabus at {dirpath}/{course_id}.md")

    # upload the md syllabus file in Azure Blob Storage
    upload_blob(
        blob_service_client=blob_service_client,
        local_filepath=str(md_filepath),
        container_name=BlobContainer.SYNTHETIC_DATA,
        base_filename=f"syllabus_{course_id}.md",
    )

    # re-split syllabus into (course>lecture>) sections
    syllabus_chunks: list[Section] = chunk_syllabus(
        syllabus_text, by="section"
    )  # type: ignore
    logger.debug("Save and uploading sections of syllabus as Azure Blobs...")

    # create course directory in syllabi directory
    course_dir = dirpath / course_id.value
    if course_dir.exists():
        shutil.rmtree(course_dir)
    course_dir.mkdir(parents=True, exist_ok=True)

    # save each section locally in the directory and upload in Azure Blobs
    for c in syllabus_chunks:
        # different file name for exercise than pure learnable content
        if not c.section_title.startswith("Exercise"):
            filename = (
                f"lecture-{c.lecture_number}-section-{c.section_number}.md"
            )
        else:
            match = re.match(r"Exercise (\d+\.\d+)", c.section_title)
            if match:
                exercise_number = match.group(1)
            else:
                raise ValueError(
                    f"Invalid exercise section title: {c.section_title}"
                )
            filename = f"exercise-{exercise_number}.md"

        chunk_filepath = dirpath / course_id.value / filename

        # save locally
        with open(chunk_filepath, "w") as f:
            f.write(c.content)

        # upload each section to Azure Blob Storage
        upload_blob(
            blob_service_client=blob_service_client,
            local_filepath=str(chunk_filepath),
            container_name=BlobContainer.SYNTHETIC_DATA,
            base_filename=f"{chunk_filepath.parent.name}/{chunk_filepath.name}",
        )


async def generate_syllabus(
    client: AsyncAzureOpenAI,
    course: Course,
    llm: LLM,
) -> str:
    """
    Generates a syllabus from the given course's basic information.
    This function does that in two steps:
    1. Generating a course outline, including lecture and section titles
    2. Generating each lecture based on the outline

    Returns a string representation of the entire syllabus.
    """

    async def generate_lecture(
        course_outline: list[LectureOutline], lecture_number: int
    ) -> str:
        """
        Generates a lecture from the syllabus, given its outline.
        The outline includes the lecture number, title, and expected sections.
        This function returns a string representation of the lecture,
        which in markdown format.
        """
        # lecture number is 1-indexed
        lecture_outline = course_outline[lecture_number - 1]
        logger.debug(f"Generating lecture: {lecture_outline.title}")

        # The following serves as context for the current lecture, to ensure
        # logical continuity in the course content. For example:
        # "Loops (for loops, while loops), Lists (slicing, indexing)"
        previous_lectures = ", ".join(
            (f"{prev_lecture.title} ({', '.join(prev_lecture.sections)})")
            for prev_lecture in course_outline[: lecture_number - 1]
        )

        # create user prompt from template
        lecture_user_prompt = LECTURE_USER_PROMPT.format(
            LECTURE_TITLE=lecture_outline.title,
            LECTURE_NUMBER=lecture_outline.lecture_number,
            MATERIAL_COVERED=", ".join(lecture_outline.sections),
            COURSE_NAME=course.name,
            COURSE_ID=course.id.value,
            PREVIOUS_LECTURES=previous_lectures,
        )
        lecture = await generate(  # LLM call
            client=client,
            system_prompt=LECTURE_SYSTEM_PROMPT,  # no placeholder
            user_prompt=lecture_user_prompt,
            llm=llm.name,
        )
        logger.info(f"Successfully generated lecture: {lecture_outline.title}")

        return lecture

    logger.debug(f"Generating syllabus for {course.id}...")
    logger.debug(f"Dividing {course.id} into lectures...")

    # course outline generation is a preliminary LLM call to propose a
    # structure to a course, including lecture titles and their section
    # titles. this is then used to generate lectures separately
    course_outline_user_prompt = COURSE_OUTLINE_USER_PROMPT.format(
        COURSE_NAME=course.name,
        COURSE_DESCRIPTION=course.description,
        N_LECTURES=course.n_lectures,
    )

    class CourseOutlineStructuredOutput(BaseModel):
        """
        An outline for a course, containing a list of lectures.
        NOTE: This class is only for Structured output purposes.
        """

        lectures: list[LectureOutline]

    course_outline = await generate(
        client=client,
        system_prompt=COURSE_OUTLINE_SYSTEM_PROMPT,
        user_prompt=course_outline_user_prompt,
        llm=llm.name,
        output_format=CourseOutlineStructuredOutput,
    )

    lecture_outlines = course_outline.lectures  # type: ignore

    # build tasks using the above helper function, in order
    # to run them concurrently
    tasks = [
        generate_lecture(lecture_outlines, i)
        for i in range(1, len(lecture_outlines) + 1)
    ]
    lectures = await asyncio.gather(*tasks)  # run tasks concurrently
    syllabus = "\n\n".join(lectures)  # form final syllabus

    # double backslashes create read issues
    syllabus = syllabus.replace("\\\\", "\\")

    logger.info("Syllabus successfully generated!\n\n")

    return syllabus

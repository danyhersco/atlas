import re
import asyncio
from pathlib import Path

from pydantic import BaseModel
from openai import AsyncAzureOpenAI
from azure.cosmos import CosmosClient

from education_data.course.search_index import chunk_syllabus
from models.base import (
    CosmosContainer,
    CourseRoadmap,
    Concept,
    Course,
    Section,
)
from utils.chat_completion import generate
from education_data.prompts import (
    LECTURE_ROADMAP_SYSTEM_PROMPT,
    LECTURE_ROADMAP_USER_PROMPT,
)
from utils.logger_config import logger
from utils.llms import LLM
from utils.azure_storage_utils import (
    upsert_cosmos,
    delete_cosmos_with_fields,
)


def save_and_upload_roadmap(
    cosmos_client: CosmosClient, course_roadmap: CourseRoadmap
) -> None:
    """
    Takes the generated Roadmap and populates Cosmos DB with its data.
    Two containers are populated: `roadmaps` and `concepts`:
    - `roadmaps`: Contains the list of concept ids
    - `concepts`: Contains the individual concepts within extended info,
        such as title, mastery criterion, section location in syllabus,
        and exercises numbers.
    """

    # Deleting existing concepts, as their ids are variable and may be
    # left over from previous runs instead of being updated.
    delete_cosmos_with_fields(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.CONCEPTS,
        fields={"course_id": course_roadmap.course_id},
    )

    # structure of document in `roadmaps` Cosmos container
    course_roadmap_json = {
        "id": course_roadmap.id,
        "course_id": course_roadmap.course_id,
        "concept_ids": [concept.id for concept in course_roadmap.concepts],
    }

    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=[course_roadmap_json],
        container_name=CosmosContainer.ROADMAPS,
    )

    all_concepts = [
        concept.model_dump(mode="json") for concept in course_roadmap.concepts
    ]
    # upload all concepts at once (azure_upload accepts multiple documents)
    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=all_concepts,
        container_name=CosmosContainer.CONCEPTS,
    )

    logger.info(
        f"Course roadmap {course_roadmap.id} and its concepts "
        "have been successfully saved to Cosmos DB."
    )


async def generate_roadmap(
    openai_client: AsyncAzureOpenAI,
    course: Course,
    llm: LLM,
) -> CourseRoadmap:
    """
    Performs course decomposition into a set of concepts (aka
    Knowledge Components or KCs), forming a course roadmap.
    In practice, it groups sequential sections with their subsequent
    exercises, and each group is fed to an LLM to generate a list of
    concepts.

    We group sections because feeding the whole course to an LLM is
    not feasible due to potential context limits and context rot risks.
    """

    # This path must exist, though the function is always called
    # after generating a syllabus.
    filepath = (
        Path(__file__).resolve().parent.parent
        / "course"
        / "syllabi"
        / f"{course.id}.md"
    )
    if not filepath.exists():
        raise FileNotFoundError(f"Syllabus file {filepath} does not exist.")

    logger.debug(f"Generating Roadmap for course {course.id}...")

    with open(filepath, "r", encoding="utf-8") as f:
        syllabus = f.read()

    logger.debug("Chunking syllabus by section...")
    sections: list[Section] = chunk_syllabus(
        syllabus,
        by="section",  # type: ignore
    )

    grouped_sections = await group_sections(sections)

    class ConceptStructuredOutput(BaseModel):
        """A temporary model for structured output of
        concept. BaseModel is required for OpenAI's
        structured output."""

        lecture_number: int
        section_number: int
        title: str
        description: str
        goal: str
        exercises: list[str]

    class ConceptListStructuredOutput(BaseModel):
        """A temporary model for structured output of
        concept list. BaseModel is required for OpenAI's
        structured output."""

        concepts: list[ConceptStructuredOutput]

    async def generate_section_group_roadmap(
        section_group: list[Section],
    ) -> list[ConceptStructuredOutput]:
        """
        Helper function to generate a list of concepts from a
        section group. This is wrapped in an async function to
        allow for concurrent processing of multiple section groups.
        """
        logger.debug(
            f"Generating roadmap for section group starting from "
            f"Lecture {section_group[0].lecture_number}, "
            f"Section {section_group[0].section_number}..."
        )
        # impute info in user prompt template
        user_prompt = LECTURE_ROADMAP_USER_PROMPT.format(
            SECTIONS="\n\n".join(
                str(section)
                for section in section_group
                if not section.section_title.startswith("Exercise")
                # hacky way to get learnable sections and not exercises
            ),
            EXERCISES="\n\n".join(
                f"{section.section_title}\n{section.content}"
                for section in section_group
                if section.section_title.startswith("Exercise")
                # hacky way to get exercises and not learnable sections
            ),
        )
        # perform LLM call to generate a list of concept
        concept_list = await generate(
            client=openai_client,
            system_prompt=LECTURE_ROADMAP_SYSTEM_PROMPT,  # no placeholders
            user_prompt=user_prompt,
            llm=llm.name,
            output_format=ConceptListStructuredOutput,
        )
        logger.info(
            f"Generated roadmap for section group starting from "
            f"Lecture {section_group[0].lecture_number}, "
            f"Section {section_group[0].section_number}..."
        )
        return concept_list.concepts  # type: ignore

    # create tasks for concurrent processing
    tasks = []
    for section_group in grouped_sections:
        tasks.append(generate_section_group_roadmap(section_group))

    concept_groups = await asyncio.gather(*tasks)  # run tasks concurrently

    logger.debug("Pooling generated concept groups into a course roadmap...")
    course_roadmap = CourseRoadmap(
        id=f"rm-{course.id}",  # id used in Cosmos DB
        course_id=course.id,
        concepts=[
            Concept(
                id=(
                    f"{'-'.join(re.sub(r'[^a-zA-Z\s]', '', concept.title).lower().split())}"  # noqa: E501
                ),  # this line format concept ID in 'this-specific-way'
                course_id=course.id,
                lecture_number=concept.lecture_number,
                section_number=concept.section_number,
                title=concept.title,
                description=concept.description,
                goal=concept.goal,
                exercises=concept.exercises,
            )
            for concept_group in concept_groups
            for concept in concept_group
        ],
    )

    logger.info(f"Generated roadmap for course {course.id}!")

    return course_roadmap


async def group_sections(sections: list[Section]) -> list[list[Section]]:
    """
    Groups sections into contiguous blocks of learnable sections and exercises.
    This strategy assumes that when an exercise included in the syllabus,
    they must test one of the previous learnable sections. We need both
    sections and exercises in a block so LLMs can link a concept to its section
    and (optional) exercises.
    """
    grouped_sections = []
    current_group = []
    for section in sections:
        if (
            current_group
            and current_group[-1].section_title.startswith("Exercise")
            and not section.section_title.startswith("Exercise")
        ):  # if we get a learnable section after an exercise, create new group
            grouped_sections.append(current_group)
            current_group = [section]
        else:
            current_group.append(section)
    if current_group:  # if we have a remaining group, add it to the list
        grouped_sections.append(current_group)

    return grouped_sections

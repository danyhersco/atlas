import os
import argparse
import asyncio
from enum import StrEnum


from education_data.course.search_index import make_syllabus_search_index
from education_data.course.data import COURSES
from education_data.workflows import (
    create_course,
    create_learner,
    reset_memory,
)
from models.base import CourseID

from education_data.learner.data import LEARNERS
from utils.clients import (
    get_aoai_client,
    get_blob_service_client,
    get_cosmos_client,
)
from utils.logger_config import logger
from utils.llms import get_llm, LLMName


class EducationDataCLIMode(StrEnum):
    """CLI endpoints for education_data module"""

    COURSE = "course"
    LEARNER = "learner"
    MEMORY = "memory"
    VECTOR_INDEX = "vector_index"


COURSE_IDS = COURSES.keys()  # list of course IDs
LEARNER_IDS = LEARNERS.keys()  # list of learner IDs


def parse_args():
    """
    Parse command-line arguments for the Education Data CLI.
    Includes checks for required/forbidden arguments based on the
    selected mode.
    """
    parser = argparse.ArgumentParser(description="Run Education Data CLI.")
    parser.add_argument(
        "mode",
        type=str,
        choices=[mode.value for mode in EducationDataCLIMode],
    )
    parser.add_argument(
        "-c",
        "--course-id",
        type=str,
        choices=list(COURSES.keys()) + ["all"],
    )
    parser.add_argument(
        "-l",
        "--learner-id",
        type=str,
        choices=list(LEARNERS.keys()) + ["all"],
    )
    parser.add_argument(
        "-m",
        "--llm",
        type=str,
        choices=[name.value for name in LLMName],
        default="gpt-4.1-mini",
        help="LLM deployment name (default: gpt-4.1-mini)",
    )
    args = parser.parse_args()

    if args.mode == EducationDataCLIMode.COURSE and not args.course_id:
        parser.error("When mode is 'course', --course-id is required.")
    if args.mode == EducationDataCLIMode.LEARNER and not args.learner_id:
        parser.error("When mode is 'learner', --learner-id is required.")
    if args.mode == EducationDataCLIMode.MEMORY and not args.course_id:
        parser.error("When mode is 'memory', --course-id is required.")
    if args.mode == EducationDataCLIMode.MEMORY and not args.learner_id:
        parser.error("When mode is 'memory', --learner-id is required.")
    if args.mode == EducationDataCLIMode.VECTOR_INDEX and not args.course_id:
        parser.error("When mode is 'vector_index', --course-id is required.")
    if args.learner_id == "all" and args.mode != EducationDataCLIMode.LEARNER:
        parser.error("--learner-id can only be 'all' when mode is 'learner'.")
    if args.course_id == "all" and args.mode != EducationDataCLIMode.COURSE:
        parser.error("--course-id can only be 'all' when mode is 'course'.")

    return args


async def main():
    """Main function to run the Education Data CLI."""
    args = parse_args()
    logger.debug(f"Selected mode: {args.mode}.")

    llm = get_llm(name=LLMName(args.llm))  # get LLM object from model name
    # lazy-load clients
    openai_client = get_aoai_client()
    cosmos_client = get_cosmos_client()
    blob_client = get_blob_service_client()
    logger.info("Azure client successfully created.")

    # create course endpoint, needs course_id arg only
    if args.mode == EducationDataCLIMode.COURSE:
        if args.course_id == "all":
            courses = list(COURSES.values())
        else:  # if not all, only one course_id will be included here
            courses = [COURSES[args.course_id]]

        for course in courses:
            await create_course(
                openai_client=openai_client,
                cosmos_client=cosmos_client,
                blob_client=blob_client,
                course=course,
                llm=llm,
            )
    # create learner endpoint, needs learner_id arg only
    elif args.mode == EducationDataCLIMode.LEARNER:
        if args.learner_id == "all":
            learners = list(LEARNERS.values())
        else:  # if not all, only one learner_id will be included here
            learners = [LEARNERS[args.learner_id]]

        for learner in learners:
            create_learner(
                cosmos_client=cosmos_client,
                learner=learner,
            )
    # reset memory endpoint, needs both learner_id and course_id args
    elif args.mode == EducationDataCLIMode.MEMORY:
        reset_memory(
            cosmos_client=cosmos_client,
            learner_id=args.learner_id,
            course_id=CourseID(args.course_id),
        )
    # reset vector index endpoint, needs course_id arg only
    elif args.mode == EducationDataCLIMode.VECTOR_INDEX:
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "course",
            "syllabi",
            f"{args.course_id}.md",
        )
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = f.read()
        make_syllabus_search_index(syllabus, args.course_id.lower())
    else:
        raise ValueError(f"Unknown CLI mode: {args.mode}")


if __name__ == "__main__":
    asyncio.run(main())  # run the CLI

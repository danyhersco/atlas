import asyncio
import argparse

from agents.atlas_agent import AtlasAgent
from education_data.workflows import reset_memory
from utils.clients import get_cosmos_client
from utils.llms import LLMName
from utils.logger_config import logger
from education_data.course.data import COURSES
from models.base import CourseID


def parse_args():
    parser = argparse.ArgumentParser(description="Run Atlas CLI.")
    parser.add_argument(
        "course_id",
        type=str,
        choices=list(COURSES.keys()),
    )
    parser.add_argument(
        "-r",
        "--reset-memory",
        action="store_true",
    )
    parser.add_argument(
        "-m",
        "--llm",
        type=str,
        choices=[name.value for name in LLMName],
        default="gpt-4.1",
        help="LLM deployment name (default: gpt-4.1)",
    )
    args = parser.parse_args()
    return args


async def main():
    args = parse_args()
    learner_id = "learner_10"  # ID dedicated to demo student
    course_id = CourseID(args.course_id)
    course = COURSES[course_id]

    logger.info(
        f"Starting Atlas CLI for course {course_id} "
        f"and model {args.llm} for ATLAS"
    )

    if args.reset_memory:
        reset_memory(
            cosmos_client=get_cosmos_client(),
            learner_id=learner_id,
            course_id=course_id,
        )

    mcp_plugin = await AtlasAgent.mcp_connect()

    am = AtlasAgent(course, learner_id, mcp_plugin, args.llm)

    logger.debug("Starting conversation...")

    while True:
        user_input = input("Me: ")

        if user_input == "exit":
            break

        print("Assistant: ", end="")

        async for chunk in am.process_learner_message(user_input):
            print(chunk, end="")

        print("\n\n")

    await AtlasAgent.mcp_disconnect(mcp_plugin)


if __name__ == "__main__":
    asyncio.run(main())

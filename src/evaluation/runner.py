"""
THIS SCRIPT IS INTENDED TO BE RUN IN A AZURE CONTAINER APP.

It is used for running simulations for different learners in a course.
The reason why it is run in a container app is that evaluation can take
a long time to complete.

For examiners: setting up all resources and instructions to be able to
run simulation in the cloud may be way too overkill. Use the local
environment through CLI for testing purposes (see README.md).
"""

import os
import sys
import asyncio
import argparse

from evaluation.simulation import LearnerType, SimulationRunner, TutoringType
from education_data.course.data import COURSES
from education_data.workflows import reset_memory
from models.base import Course, CourseID
from utils.clients import get_cosmos_client
from utils.logger_config import logger


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    get = os.getenv
    p.add_argument("--tutoring-type", default=get("TUTORING_TYPE", "atlas"))
    p.add_argument("--teacher-model", default=get("TEACHER_MODEL", "gpt-4.1"))
    p.add_argument("--learner-model", default=get("LEARNER_MODEL", "gpt-4.1"))
    p.add_argument(
        "--max-chat-rounds",
        type=int,
        default=int(get("MAX_CHAT_ROUNDS", "10")),
    )
    p.add_argument(
        "--shard-index", type=int, default=int(get("SHARD_INDEX", "0"))
    )
    return p.parse_args()


async def run_simulation_for_learner(
    learner_id: str,
    course: Course,
    tutoring_type: TutoringType,
    teacher_model: str,
    learner_model: str,
    max_chat_rounds: int,
) -> None:
    """
    Wrapper to re-init memory and start simulation
    from the beginning of the course.
    """
    cosmos_client = get_cosmos_client()
    reset_memory(cosmos_client, learner_id, course.id)
    simulation_runner = SimulationRunner(
        course, learner_id, teacher_model, learner_model
    )
    await simulation_runner.run_simulation(
        LearnerType.SK, tutoring_type, max_chat_rounds, verbose=False
    )


async def main():
    args = parse_args()
    course = COURSES[CourseID.PYT101]
    learner_ids = [f"learner_{i + 1}" for i in range(9)]
    idx_str = os.getenv("SHARD_INDEX", "not found")
    try:
        idx = int(idx_str)
    except ValueError:
        logger.critical(f"Invalid SHARD_INDEX={idx_str!r}")
        sys.exit(1)

    logger.critical(
        f"Config:\ncourse={course.id}\nteacher_model={args.teacher_model}\n"
        f"learner_model={args.learner_model}\nmax_rounds="
        f"{args.max_chat_rounds}\nshard_index={args.shard_index}"
    )

    if not (0 <= idx < len(learner_ids)):
        logger.critical(
            f"Replica index {idx} out of range for "
            f"{len(learner_ids)} learners."
        )
        sys.exit(1)

    learner_id = learner_ids[idx]
    logger.critical(f"Replica index {idx} assigned learner: {learner_id}")

    try:
        logger.critical(f"Starting simulation for {learner_id}")
        await run_simulation_for_learner(
            learner_id=learner_id,
            course=course,
            tutoring_type=TutoringType(args.tutoring_type),
            teacher_model=args.teacher_model,
            learner_model=args.learner_model,
            max_chat_rounds=args.max_chat_rounds,
        )
        logger.critical(f"Done simulation for {learner_id}.")
    except Exception as e:
        logger.critical(
            f"Error while running {learner_id}: {type(e).__name__}: {e}"
        )
        sys.exit(2)


if __name__ == "__main__":
    asyncio.run(main())

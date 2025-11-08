from enum import StrEnum
import asyncio
import argparse

from evaluation.exam import ExamTaker
from education_data.learner.data import LEARNERS
from education_data.course.data import COURSES
from evaluation.simulation import LearnerType, SimulationRunner
from evaluation.stats import StatisticsCalculator
from models.base import CourseID
from utils.llms import LLMName
from utils.logger_config import logger


class EvaluationCLIMode(StrEnum):
    SIMULATION = "simulation"
    EXAM = "exam"
    STATISTICS = "stats"


def parse_args():
    parser = argparse.ArgumentParser(description="SAILED Evaluation CLI.")
    parser.add_argument(
        "mode",
        type=str,
        choices=[mode.value for mode in EvaluationCLIMode],
    )
    parser.add_argument(
        "-l",
        "--learner-id",
        type=str,
        choices=list(LEARNERS.keys()) + ["all"],
    )
    parser.add_argument(
        "-t",
        "--tutoring-type",
        type=str,
        choices=["atlas", "vanilla"],
    )
    parser.add_argument(
        "-n",
        "--max-chat-rounds",
        type=int,
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

    if args.mode == EvaluationCLIMode.SIMULATION and not args.learner_id:
        parser.error("When mode is 'simulation', --learner-id is required.")
    if args.mode == EvaluationCLIMode.SIMULATION and not args.tutoring_type:
        parser.error("When mode is 'simulation', --tutoring-type is required.")
    if args.mode == EvaluationCLIMode.SIMULATION and not args.max_chat_rounds:
        parser.error(
            "When mode is 'simulation', --max-chat-rounds is required."
        )
    if args.mode == EvaluationCLIMode.EXAM and not args.learner_id:
        parser.error("When mode is 'exam', --learner-id is required.")
    if args.learner_id == "all" and args.mode != EvaluationCLIMode.EXAM:
        parser.error("--learner-id can only be 'all' when mode is 'exam'.")
    if args.learner_id == "learner_10":
        parser.error("learner_10 is reserved for demo only.")

    return args


async def main():
    args = parse_args()
    logger.debug(f"Selected mode: {args.mode}.")

    if args.mode == EvaluationCLIMode.SIMULATION:
        course = COURSES[CourseID.PYT101]
        learner_id = args.learner_id
        learner_type = LearnerType.SK
        tutoring_type = args.tutoring_type
        teacher_model = args.llm
        learner_model = args.llm
        max_chat_rounds = args.max_chat_rounds

        simulation_runner = SimulationRunner(
            course, learner_id, teacher_model, learner_model
        )
        await simulation_runner.run_simulation(
            learner_type, tutoring_type, max_chat_rounds
        )

    elif args.mode == EvaluationCLIMode.EXAM:
        if args.learner_id == "all":
            learner_ids = list(LEARNERS.keys())
        else:
            learner_ids = [args.learner_id]

        for learner_id in learner_ids:
            await ExamTaker.run_exam_taking(learner_id, args.llm)

    elif args.mode == EvaluationCLIMode.STATISTICS:
        statistics_calculator = StatisticsCalculator()
        statistics_calculator.calculate_eval_stats()

    else:
        raise ValueError(f"Unknown mode: {args.mode}")


if __name__ == "__main__":
    asyncio.run(main())

import json
import asyncio
from pathlib import Path
from typing import Literal

from pydantic import BaseModel
import pandas as pd

from education_data.learner.data import LEARNERS
from evaluation.simulation import TutoringType
from education_data.course.data import COURSES
from models.base import (
    BlobContainer,
    ChatSession,
    ConceptChat,
    ConceptProfile,
    CosmosContainer,
    Course,
    CourseID,
    ExamQuestion,
    ExamRequest,
    ExamResult,
    Learner,
)
from utils.azure_storage_utils import get_blob, get_cosmos_docs_with_ids
from utils.clients import (
    get_aoai_client,
    get_blob_service_client,
    get_cosmos_client,
)
from utils.llms import LLM, LLMName, get_llm
from utils.chat_completion import generate
from utils.logger_config import logger


class ExamTaker:
    def __init__(
        self,
        llm: LLM,
        learner: Learner,
        course: Course = COURSES[CourseID.PYT101],
    ):
        self.llm = llm
        self.learner = learner
        self.course = course

        self.cosmos_client = get_cosmos_client()

        self.concept_profile = ConceptProfile(
            **get_cosmos_docs_with_ids(
                cosmos_client=self.cosmos_client,
                container_name=CosmosContainer.CONCEPT_PROFILES,
                document_ids=[f"cp-{self.learner.id}"],
            )[0]
        )

        blob_service_client = get_blob_service_client()
        self.exam_questions = [
            ExamQuestion(**exam_question)
            for exam_question in json.loads(
                get_blob(
                    blob_service_client=blob_service_client,
                    container_name=BlobContainer.SYNTHETIC_DATA,
                    blob_name=f"exam_{self.course.id}.json",
                )
            )
        ]

        self.openai_client = get_aoai_client()

    async def predict_exam_results(
        self,
        tutoring_type: TutoringType,
    ) -> list[ExamResult]:
        """
        Predict exam results for learner.

        This method prepares question answering requests for each concept,
        including knowledge status prior to enrolling in the course,
        tutoring conversation, and exam questions. For each concept, it
        sends a prompt to a third party LLM behaving as the "Psychologist",
        who predicts what the learner would answer based on the prior level
        and newly acquired knowledge.

        Args:
            tutoring_type (TutoringType): The type of tutoring agent used for
                the exam (NO_TUTORING, VANILLA, or ATLAS).

        Returns:
            list[ExamResult]: A list of exam results, each containing the
                concept ID, prior level, question, choices, selected answer,
                and reasoning.

        Raises:
            TypeError: If the LLM response does not match the expected output
                format.
            ValueError: If prior level or exam question cannot be determined
                for a concept.
        """
        # get question answering system prompt template
        exam_system_file = (
            Path(__file__).resolve().parent
            / "instructions"
            / "exam_system.txt"
        )
        with open(exam_system_file, "r") as f:
            exam_system = f.read().strip()

        # get question answering system prompt template
        exam_user_file = (
            Path(__file__).resolve().parent / "instructions" / "exam_user.txt"
        )
        with open(exam_user_file, "r") as f:
            exam_user = f.read().strip()

        class ExamResultStructuredOutput(BaseModel):
            """Used only for structured output of exam results"""

            reasoning: str
            answer: Literal["A", "B", "C", "D", "E"]

        async def take_question(exam_request: ExamRequest):
            """Helper function to generate exam answers concurrently"""
            logger.debug(
                f"Taking exam question for concept: {exam_request.concept_id}"
            )
            exam_system_formatted = exam_system.format(
                COURSE_NAME=self.course.name,
                CONCEPT_NAME=exam_request.concept_id,
            )
            # format the user prompt with the exam request details
            exam_user_formatted = exam_user.format(
                PRIOR_LEVEL=exam_request.prior_level,
                TUTORING_CONVERSATION=json.dumps(
                    [message.model_dump() for message in exam_request.messages]
                ),
                EXAM_QUESTION=exam_request.exam_question,
            )
            # generate question answer
            response = await generate(
                client=self.openai_client,
                system_prompt=exam_system_formatted,
                user_prompt=exam_user_formatted,
                llm=self.llm.name,
                output_format=ExamResultStructuredOutput,
            )
            logger.debug(
                "Got exam question response for "
                f"concept {exam_request.concept_id}"
            )
            return response

        exam_requests = self._form_exam_requests(tutoring_type)

        # make tasks and run concurrently
        responses = await asyncio.gather(
            *[take_question(req) for req in exam_requests],
        )

        exam_results = []
        for req, res in zip(exam_requests, responses):
            if not isinstance(res, ExamResultStructuredOutput):
                raise TypeError(f"Unexpected response format: {type(req)}")

            exam_results.append(
                ExamResult(
                    concept_id=req.concept_id,
                    prior_level=req.prior_level,
                    question=req.exam_question.question,
                    choices=req.exam_question.choices,
                    answer=res.answer,
                    reasoning=res.reasoning,
                )
            )

        return exam_results

    def _form_exam_requests(
        self,
        tutoring_type: TutoringType,
    ) -> list[ExamRequest]:
        """
        Groups prior knowledge status, tutoring conversation, and
        exam question for each concept.

        This method prepares a list of ExamRequest objects for the
        learner, combining:
        - The learner's prior knowledge level for each concept
        - The tutoring conversation messages for each concept (if available)
        - The corresponding exam question for each concept

        Args:
            tutoring_type (TutoringType): The type of tutoring agent used
                for the exam (NO_TUTORING, VANILLA, or ATLAS).

        Returns:
            list[ExamRequest]: A list of ExamRequest objects, each containing
                the concept ID, prior level, conversation messages,
                and exam question.

        Raises:
            ValueError: If prior level or exam question cannot be determined
                for a concept.
        """

        def find_prior_knowledge_status(concept_id: str) -> str:
            """Helper function to find the student's knowledge
            status in the concept, prior to enrolling the course"""
            if concept_id in self.concept_profile.not_started:
                return "not_started"
            elif concept_id in self.concept_profile.confused:
                return "confused"
            elif concept_id in self.concept_profile.mastered:
                return "mastered"
            raise ValueError(f"Unknown prior level for concept {concept_id}")

        def find_exam_question(concept_id: str) -> ExamQuestion:
            """Helper function to find the exam question testing
            the concept_id entered"""
            for question in self.exam_questions:
                if question.concept_id == concept_id:
                    return question
            raise ValueError(
                f"No exam question found for concept {concept_id}"
            )

        # empty concept messages if no tutoring
        if tutoring_type == TutoringType.NO_TUTORING:
            concept_chats = [
                ConceptChat(concept_id=q.concept_id, messages=[])
                for q in self.exam_questions
            ]
        # split chat session by dev message to get concept-specific messages
        else:
            concept_chats = ExamTaker.group_messages_by_concept(
                learner_id=self.learner.id,
                tutoring_type=tutoring_type,
            )
        exam_requests = []

        # an exam request contains prior status, messages, and exam question,
        # all related to a specific concept of the course
        for chat in concept_chats:
            prior_level = find_prior_knowledge_status(chat.concept_id)
            exam_question = find_exam_question(chat.concept_id)

            exam_requests.append(
                ExamRequest(
                    concept_id=chat.concept_id,
                    prior_level=prior_level,
                    messages=chat.messages,
                    exam_question=exam_question,
                )
            )

        return exam_requests

    @staticmethod
    def group_messages_by_concept(
        learner_id: str,
        tutoring_type: TutoringType,
    ) -> list[ConceptChat]:
        """
        Groups chat session messages by concept, using the chat
        session record from the learner and tutoring type.

        This method loads the chat session from `chat_sessions/`,
        splits messages into groups based on concept delimiters
        (dev messages), and returns a list of ConceptChat objects,
        each containing the concept ID and its associated messages.

        Args:
            learner_id (str): The ID of the learner whose chat session
                to process.
            tutoring_type (TutoringType): The type of tutoring agent used
                in the session.

        Returns:
            list[ConceptChat]: A list of ConceptChat objects, each containing
                a concept ID and the corresponding messages for that concept.

        Raises:
            ValueError: If a message appears before any concept delimiter.
        """
        filepath = (
            Path(__file__).resolve().parent
            / "chat_sessions"
            / f"{learner_id}_{tutoring_type}_sim.json"
        )
        with open(filepath, "r") as f:
            chat_session = ChatSession(**json.load(f))
        concept_chats = []
        current_concept_id = None
        current_messages = []

        for message in chat_session.messages:
            if message.role == "dev":
                # If we already have a concept in progress, save it
                if current_concept_id is not None:
                    concept_chats.append(
                        ConceptChat(
                            concept_id=current_concept_id,
                            messages=current_messages,
                        )
                    )
                # Start a new concept group
                current_concept_id = message.content
                current_messages = []
            else:
                # Add messages to the current concept
                if current_concept_id is not None:
                    current_messages.append(message)
                else:
                    raise ValueError("Message came before any concept!")

        # Add the last group if any
        if current_concept_id is not None:
            concept_chats.append(
                ConceptChat(
                    concept_id=current_concept_id,
                    messages=current_messages,
                )
            )

        return concept_chats

    @staticmethod
    async def run_exam_taking(learner_id: str, model_name: str):
        """
        Runs the exam-taking process for a learner across all tutoring types.

        This method creates an ExamTaker instance for the specified
        learner and model, predicts exam results for each tutoring type
        (no tutoring, vanilla, atlas), saves markdown reports for each,
        and exports all results to a CSV file.

        Args:
            learner_id (str): The ID of the learner to take the exam.
            model_name (str): The LLM deployment name to use for exam
                prediction.

        Returns:
            None
        """
        exam_taker = ExamTaker(
            llm=get_llm(LLMName(model_name)),
            learner=LEARNERS[learner_id],
        )

        # no tutoring
        no_tutoring_exam_results = await exam_taker.predict_exam_results(
            TutoringType.NO_TUTORING,
        )
        ExamTaker.save_exam_report_md(
            no_tutoring_exam_results, TutoringType.NO_TUTORING, learner_id
        )

        # vanilla tutoring
        vanilla_exam_results = await exam_taker.predict_exam_results(
            TutoringType.VANILLA,
        )
        ExamTaker.save_exam_report_md(
            vanilla_exam_results, TutoringType.VANILLA, learner_id
        )

        # atlas tutoring
        atlas_exam_results = await exam_taker.predict_exam_results(
            TutoringType.ATLAS,
        )

        ExamTaker.save_exam_report_md(
            atlas_exam_results, TutoringType.ATLAS, learner_id
        )

        ExamTaker.save_exam_results_csv(
            learner_id=learner_id,
            no_tutoring_results=no_tutoring_exam_results,
            vanilla_results=vanilla_exam_results,
            atlas_results=atlas_exam_results,
        )

    @staticmethod
    def save_exam_report_md(
        exam_results: list[ExamResult],
        tutoring_type: TutoringType,
        learner_id: str,
    ):
        """
        Generates and saves a markdown exam report.

        This method creates a markdown file summarizing the exam results,
        including the total number of correct answers, each question,
        choices, selected answer, and reasoning.
        The report is saved in the `exam_reports` directory.

        Args:
            exam_results (list[ExamResult]): List of exam results for
                the learner.
            tutoring_type (TutoringType): The type of tutoring agent
                used for the exam.
            learner_id (str): The ID of the learner.

        Returns:
            None
        """
        # create folder if it doesn't exist
        reports_dir = Path(__file__).resolve().parent / "exam_reports"
        reports_dir.mkdir(exist_ok=True)

        # init with first introductory line
        md_lines = [f"# Exam Report for {learner_id} - {tutoring_type}\n"]

        # get number of correct answers
        n_good_ans = 0
        for res in exam_results:
            if res.answer == "A":  # correct answer is always option A
                n_good_ans += 1

        # append exam score to report
        md_lines.append(
            f"**Total Correct Answers:** {n_good_ans}/{len(exam_results)} "
            f"({n_good_ans / len(exam_results) * 100:.2f}%)\n"
        )

        # append all questions and answers including choice and reasoning
        for idx, res in enumerate(exam_results, 1):
            md_lines.append(f"## Question {idx}: {res.concept_id}\n")
            md_lines.append(f"**Question:** {res.question}\n")
            md_lines.append("**Choices:**")
            for choice in res.choices:
                md_lines.append(f"- {choice}")
            md_lines.append(f"\n**Answer:** {res.answer}")
            md_lines.append(f"\n**Reasoning:** {res.reasoning}\n")

        file_path = reports_dir / f"{learner_id}_{tutoring_type}.md"
        with open(file_path, "w") as f:
            f.write("\n".join(md_lines))

    @staticmethod
    def save_exam_results_csv(
        learner_id: str,
        no_tutoring_results: list[ExamResult],
        vanilla_results: list[ExamResult],
        atlas_results: list[ExamResult],
    ) -> None:
        """
        Saves all exam results for a learner to a CSV file.

        This method aggregates exam results from all tutoring types
        (no tutoring, vanilla, atlas) into a single CSV file. Each
        row contains the learner ID, tutoring type, concept ID, prior
        knowledge level, question number, and selected answer. The
        file is saved in the `exam_results` directory.

        Args:
            learner_id (str): The ID of the learner.
            no_tutoring_results (list[ExamResult]): Exam results for
                no tutoring.
            vanilla_results (list[ExamResult]): Exam results for
                vanilla tutoring.
            atlas_results (list[ExamResult]): Exam results for
                atlas tutoring.

        Returns:
            None
        """
        results_dir = Path(__file__).resolve().parent / "exam_results"
        results_dir.mkdir(exist_ok=True)

        records = []
        for i, res in enumerate(no_tutoring_results, start=1):
            # no tutoring rows
            records.append(
                {
                    "learner_id": learner_id,
                    "tutoring_type": TutoringType.NO_TUTORING,
                    "concept_id": res.concept_id,
                    "prior_level": res.prior_level,
                    "question_number": i,
                    "choice": res.answer,
                }
            )
        for i, res in enumerate(vanilla_results, start=1):
            # vanilla tutoring rows
            records.append(
                {
                    "learner_id": learner_id,
                    "tutoring_type": TutoringType.VANILLA,
                    "concept_id": res.concept_id,
                    "prior_level": res.prior_level,
                    "question_number": i,
                    "choice": res.answer,
                }
            )
        for i, res in enumerate(atlas_results, start=1):
            # atlas tutoring rows
            records.append(
                {
                    "learner_id": learner_id,
                    "tutoring_type": TutoringType.ATLAS,
                    "concept_id": res.concept_id,
                    "prior_level": res.prior_level,
                    "question_number": i,
                    "choice": res.answer,
                }
            )
        df = pd.DataFrame(records)
        filepath = results_dir / f"{learner_id}_results.csv"
        df.to_csv(filepath, index=False)

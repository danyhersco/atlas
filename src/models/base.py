from pydantic import BaseModel
from enum import Enum, StrEnum
from datetime import datetime, timezone


class CourseID(StrEnum):
    MAT901 = "MAT901"
    ECO901 = "ECO901"
    LAW901 = "LAW901"
    COM901 = "COM901"
    FIN901 = "FIN901"
    PYT101 = "PYT101"


class Course(BaseModel):
    """
    A Course object that includes basic information to represent it.
    """

    id: CourseID
    name: str
    description: str
    n_lectures: int
    syllabus_url: str
    exam_url: str


class LectureOutline(BaseModel):
    """
    An outline for a single lecture, containing the lecture number,
    title, and sections. It does not include the actual learnable
    content.
    """

    lecture_number: int
    title: str
    sections: list[str]


class Section(BaseModel):
    """A chunk of syllabus content, representing a section of a lecture."""

    id: str  # TODO: do we need?
    lecture_number: int
    lecture_title: str
    section_number: int
    section_title: str
    content: str

    def __str__(self) -> str:
        return (
            f"Lecture {self.lecture_number}: {self.lecture_title}\n"
            f"Section {self.section_number}: {self.section_title}\n\n"
            f"{self.content}"
        )


class EmbeddedSection(Section):
    """
    A syllabus chunk with an embedding for semantic search.
    This class extends Section to include an embedding vector.
    This class is used to persist the object into the vector index
    (more precisely Azure AI Search).
    """

    embedding: list[float]


class Lecture(BaseModel):
    """A chunk of syllabus content, representing a lecture of the syllabus."""

    id: str  # TODO: do we need?
    number: int
    title: str
    content: str

    def __str__(self) -> str:
        return f"Lecture {self.number}: {self.title}\n\n{self.content}"


class ExamQuestion(BaseModel):
    """
    A question for the exam, with a question text and multiple choices.
    Note that the first choice is considered the correct answer.
    """

    concept_id: str
    question: str
    choices: list[str]

    def __str__(self):
        return (
            f"Question: {self.question}\n\n"
            f"Choices: {'\n'.join(self.choices)}\n\n"
            f"Answer: {self.choices[0]}"
        )


class Concept(BaseModel):
    id: str
    course_id: CourseID
    lecture_number: int
    section_number: int
    title: str
    description: str
    goal: str
    exercises: list[str]


class CourseRoadmap(BaseModel):
    id: str
    course_id: CourseID
    concepts: list[Concept]

    def len_concepts(self):
        return len(self.concepts)


class ConceptProfile(BaseModel):
    id: str
    learner_id: str
    course_id: CourseID
    not_started: list[str]
    confused: list[str]
    mastered: list[str]


class LearnerLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Learner(BaseModel):
    id: str
    name: str
    programme: str
    course_ids: list[CourseID]
    learning_preferences: dict[CourseID, list[str]]
    level: LearnerLevel | None = None  # optional (only for eval purpose)


class ConceptStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"
    CONFUSED = "confused"


class LearnerProgress(BaseModel):
    id: str
    course_id: CourseID
    concept_id: str
    learner_id: str
    status: ConceptStatus
    evidence: str | None = None
    last_updated: datetime | None = None


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatSession(BaseModel):
    id: str
    course_id: CourseID
    learner_id: str
    atlas_model: str
    messages: list[ChatMessage]
    last_opened: str = datetime.now(timezone.utc).isoformat()


class CheckpointList(BaseModel):
    id: str
    course_id: str
    learner_id: str
    checkpoints: list[str]


class ConceptChat(BaseModel):
    concept_id: str
    messages: list[ChatMessage]


class ExamRequest(ConceptChat):
    prior_level: str
    exam_question: ExamQuestion


class ExamResult(BaseModel):
    concept_id: str
    prior_level: str
    question: str
    choices: list[str]
    answer: str
    reasoning: str


class CosmosContainer(StrEnum):
    CHAT_SESSIONS = "chat_sessions"
    CHECKPOINTS = "checkpoints"
    CONCEPTS = "concepts"
    CONCEPT_PROFILES = "concept_profiles"
    COURSES = "courses"
    LEARNERS = "learners"
    PROGRESSES = "progresses"
    ROADMAPS = "roadmaps"


class BlobContainer(StrEnum):
    CHAT_REPORTS = "chat-reports"
    SYNTHETIC_DATA = "synthetic-data"

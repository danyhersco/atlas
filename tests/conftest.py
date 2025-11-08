import os
import pytest
from unittest.mock import AsyncMock

from models.base import Course, CourseID, ExamQuestion, Learner, LearnerLevel
from utils.llms import LLM


@pytest.fixture
def mock_course():
    return Course(
        id=CourseID.MAT901,
        name="fake name",
        description="fake description",
        n_lectures=2,
        syllabus_url="https://www.fakeurl.com/",
        exam_url="https://www.fakeurl.com/",
    )


@pytest.fixture
def mock_learner():
    return Learner(
        id="learner1",
        name="Test Learner",
        programme="Computer Science",
        course_ids=[CourseID.MAT901],
        learning_preferences={CourseID.MAT901: ["visual", "hands-on"]},
        level=LearnerLevel.BEGINNER,
    )


@pytest.fixture
def mock_cosmos_client():
    return AsyncMock()


@pytest.fixture
def mock_web_content():
    return "Fake web content"


@pytest.fixture
def mock_llm():
    return LLM(name="fake_name", key="fake_key", endpoint="fake_endpoint")


@pytest.fixture
def mock_client():
    return AsyncMock()


@pytest.fixture
def mock_syllabus():
    return "# Lecture 1: Fake Lecture\n\n## 1.1 Fake Section\n\nFake Content."


@pytest.fixture
def mock_exam():
    return [
        ExamQuestion(
            concept_id="concept1",
            question="What is 2 + 2?",
            choices=["3", "4", "5", "6", "7"],
        )
    ]


@pytest.fixture
def mock_html():
    return "<html><body><p>Hello world</p></body></html>"


@pytest.fixture
def mock_url():
    return "https://example.com"


@pytest.fixture(autouse=True)
def set_env_vars():
    os.environ["BLOB_STORAGE_URL"] = "https://fakeurl"
    os.environ["COSMOS_URI"] = "https://fakecosmos"
    os.environ["COSMOS_KEY"] = "fakekey"

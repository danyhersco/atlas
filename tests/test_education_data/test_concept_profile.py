import pytest
from unittest.mock import patch

from education_data.learner.concept_profile import (
    reset_concept_profile_in_cosmos,
)
from models.base import Learner, CourseID, LearnerLevel


@pytest.fixture
def mock_concept_ids():
    return [
        "concept1",
        "concept2",
        "concept3",
        "concept4",
        "concept5",
        "concept6",
        "concept7",
        "concept8",
        "concept9",
        "concept10",
    ]


@pytest.fixture
def mock_beginner_learner():
    return Learner(
        id="learner1",
        name="Test Beginner",
        programme="Computer Science",
        course_ids=[CourseID.PYT101],
        learning_preferences={CourseID.PYT101: ["visual", "hands-on"]},
        level=LearnerLevel.BEGINNER,
    )


@patch("education_data.learner.concept_profile.upsert_cosmos")
@patch("education_data.learner.concept_profile.get_cosmos_docs_with_ids")
@patch("education_data.learner.concept_profile.random.shuffle")
def test_reset_concept_profile_beginner_learner(
    mock_shuffle,
    mock_get_cosmos_docs,
    mock_upsert_cosmos,
    mock_cosmos_client,
    mock_beginner_learner,
    mock_concept_ids,
):
    """Test the reset_concept_profile_in_cosmos
    function for a BEGINNER level learner."""

    # Mock the cosmos response
    mock_get_cosmos_docs.return_value = [{"concept_ids": mock_concept_ids}]

    # Mock random.shuffle to not actually shuffle (for predictable testing)
    mock_shuffle.return_value = None

    reset_concept_profile_in_cosmos(mock_cosmos_client, mock_beginner_learner)

    # Verify that get_cosmos_docs_with_ids was called correctly
    mock_get_cosmos_docs.assert_called_once_with(
        cosmos_client=mock_cosmos_client,
        container_name="roadmaps",
        document_ids=[f"rm-{mock_beginner_learner.course_ids[0]}"],
    )

    # Verify that upsert_cosmos was called
    mock_upsert_cosmos.assert_called_once()

    # Get the call arguments
    call_args = mock_upsert_cosmos.call_args
    assert call_args[1]["cosmos_client"] == mock_cosmos_client
    assert call_args[1]["container_name"] == "concept_profiles"
    assert len(call_args[1]["documents"]) == 1

    # Check the concept profile structure
    concept_profile = call_args[1]["documents"][0]
    assert concept_profile["id"] == f"cp-{mock_beginner_learner.id}"
    assert concept_profile["learner_id"] == mock_beginner_learner.id
    assert concept_profile["course_id"] == mock_beginner_learner.course_ids[0]

    # For BEGINNER: 10% mastered, 50% confused, 40% not started
    # With 10 concepts: 1 mastered, 5 confused, 4 not started
    assert len(concept_profile["mastered"]) == 1
    assert len(concept_profile["confused"]) == 5
    assert len(concept_profile["not_started"]) == 4

    # Verify all concepts are accounted for
    all_concepts = (
        concept_profile["mastered"]
        + concept_profile["confused"]
        + concept_profile["not_started"]
    )
    assert len(all_concepts) == len(mock_concept_ids)
    assert set(all_concepts) == set(mock_concept_ids)


@patch("education_data.learner.concept_profile.upsert_cosmos")
@patch("education_data.learner.concept_profile.get_cosmos_docs_with_ids")
def test_reset_concept_profile_multi_course_learner(
    mock_get_cosmos_docs,
    mock_upsert_cosmos,
    mock_cosmos_client,
):
    """Test reset_concept_profile_in_cosmos for a
    learner enrolled in multiple courses."""

    multi_course_learner = Learner(
        id="learner4",
        name="Test Multi-Course",
        programme="Computer Science",
        course_ids=[CourseID.PYT101, CourseID.MAT901],
        learning_preferences={
            CourseID.PYT101: ["visual", "hands-on"],
            CourseID.MAT901: ["theoretical", "practical"],
        },
        level=LearnerLevel.BEGINNER,
    )

    reset_concept_profile_in_cosmos(mock_cosmos_client, multi_course_learner)

    # For multi-course learners, the function
    # should return early without creating a profile
    mock_upsert_cosmos.assert_not_called()
    mock_get_cosmos_docs.assert_not_called()

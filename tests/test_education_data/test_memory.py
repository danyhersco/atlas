from unittest.mock import patch

from education_data.memory.checkpoint import reset_checkpoints_in_cosmos
from education_data.memory.progress import reset_progress_in_cosmos
from models.base import CourseID


@patch("education_data.memory.checkpoint.upsert_cosmos")
def test_reset_checkpoints_in_cosmos(mock_upsert_cosmos, mock_cosmos_client):
    """Test the reset_checkpoints_in_cosmos function."""

    learner_id = "learner1"
    course_id = CourseID.MAT901

    reset_checkpoints_in_cosmos(learner_id, course_id, mock_cosmos_client)

    # Verify that upsert_cosmos was called
    mock_upsert_cosmos.assert_called_once()

    # Get the call arguments
    call_args = mock_upsert_cosmos.call_args
    assert call_args[1]["cosmos_client"] == mock_cosmos_client
    assert call_args[1]["container_name"] == "checkpoints"
    assert len(call_args[1]["documents"]) == 1

    # Check the checkpoint list structure
    checkpoint_list = call_args[1]["documents"][0]
    assert checkpoint_list["id"] == f"checkpoints-{course_id}-{learner_id}"
    assert checkpoint_list["course_id"] == course_id
    assert checkpoint_list["learner_id"] == learner_id
    assert checkpoint_list["checkpoints"] == []  # Should be empty list


@patch("education_data.memory.progress.upsert_cosmos")
@patch("education_data.memory.progress.delete_cosmos_with_fields")
@patch("education_data.memory.progress.get_cosmos_docs_with_ids")
def test_reset_progress_in_cosmos(
    mock_get_cosmos_docs,
    mock_delete_cosmos,
    mock_upsert_cosmos,
    mock_cosmos_client,
):
    """Test the reset_progress_in_cosmos function."""

    learner_id = "learner1"
    course_id = CourseID.MAT901

    # Mock the concept IDs returned from the roadmap
    mock_concept_ids = ["concept1", "concept2", "concept3"]
    mock_get_cosmos_docs.return_value = [{"concept_ids": mock_concept_ids}]

    reset_progress_in_cosmos(learner_id, course_id, mock_cosmos_client)

    # Verify that get_cosmos_docs_with_ids was called to get concept IDs
    mock_get_cosmos_docs.assert_called_once_with(
        cosmos_client=mock_cosmos_client,
        container_name="roadmaps",
        document_ids=[f"rm-{course_id}"],
    )

    # Verify that delete_cosmos_with_fields
    # was called to delete existing progress
    mock_delete_cosmos.assert_called_once_with(
        cosmos_client=mock_cosmos_client,
        container_name="progresses",
        fields={"course_id": course_id, "learner_id": learner_id},
    )

    # Verify that upsert_cosmos was called to upload new progress entries
    mock_upsert_cosmos.assert_called_once()

    # Get the call arguments
    call_args = mock_upsert_cosmos.call_args
    assert call_args[1]["cosmos_client"] == mock_cosmos_client
    assert call_args[1]["container_name"] == "progresses"
    assert len(call_args[1]["documents"]) == 3  # One for each concept

    # Check the progress entries structure
    progress_entries = call_args[1]["documents"]
    for i, progress in enumerate(progress_entries):
        assert progress["id"] == f"{learner_id}-{mock_concept_ids[i]}"
        assert progress["course_id"] == course_id
        assert progress["concept_id"] == mock_concept_ids[i]
        assert progress["learner_id"] == learner_id
        assert (
            progress["status"] == "not_started"
        )  # The enum value as a string

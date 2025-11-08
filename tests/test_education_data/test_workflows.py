import pytest
from unittest.mock import patch, AsyncMock

from education_data.workflows import (
    create_course,
    create_learner,
    reset_memory,
)


@pytest.mark.asyncio
@patch("education_data.workflows.upsert_cosmos")
@patch("education_data.workflows.save_and_upload_exam")
@patch(
    "education_data.workflows.generate_exam",
    new_callable=AsyncMock,
)
@patch("education_data.workflows.make_syllabus_search_index")
@patch("education_data.workflows.save_and_upload_syllabus")
@patch(
    "education_data.workflows.generate_syllabus",
    new_callable=AsyncMock,
)
@patch("education_data.workflows.generate_roadmap")
@patch("education_data.workflows.save_and_upload_roadmap")
@patch("education_data.workflows.reset_progress_in_cosmos")
@patch("education_data.workflows.reset_concept_profile_in_cosmos")
@patch("education_data.workflows.reset_checkpoints_in_cosmos")
@patch("education_data.workflows.CosmosClient")
@patch("education_data.workflows.BlobServiceClient")
@patch("education_data.workflows.AsyncAzureOpenAI")
async def test_create_course(
    mock_openai_client,
    mock_blob_client,
    mock_cosmos_client,
    mock_reset_checkpoints,
    mock_reset_concept_profile,
    mock_reset_progress,
    mock_save_and_upload_roadmap,
    mock_generate_roadmap,
    mock_generate_syllabus,
    mock_save_and_upload_syllabus,
    mock_make_syllabus_search_index,
    mock_generate_exam,
    mock_save_and_upload_exam,
    mock_upsert_cosmos,
    mock_course,
    mock_llm,
    mock_syllabus,
    mock_exam,
    mock_learner,
):
    # Mock return values
    mock_generate_syllabus.return_value = mock_syllabus
    mock_generate_exam.return_value = mock_exam
    mock_generate_roadmap.return_value = {
        "concept_ids": ["concept1", "concept2"]
    }

    # Mock the LEARNERS data that the function uses
    with patch(
        "education_data.workflows.LEARNERS", {"learner1": mock_learner}
    ):
        await create_course(
            mock_openai_client,
            mock_cosmos_client,
            mock_blob_client,
            mock_course,
            mock_llm,
        )

    # Verify syllabus generation and saving
    mock_generate_syllabus.assert_called_once_with(
        client=mock_openai_client,
        course=mock_course,
        llm=mock_llm,
    )
    mock_save_and_upload_syllabus.assert_called_once_with(
        mock_syllabus, mock_course.id, mock_blob_client
    )

    # Verify search index creation
    mock_make_syllabus_search_index.assert_called_once_with(
        syllabus=mock_syllabus,
        index_name=mock_course.id.lower(),
    )

    # Verify roadmap generation and saving
    mock_generate_roadmap.assert_called_once_with(
        openai_client=mock_openai_client,
        course=mock_course,
        llm=mock_llm,
    )
    mock_save_and_upload_roadmap.assert_called_once_with(
        cosmos_client=mock_cosmos_client,
        course_roadmap={"concept_ids": ["concept1", "concept2"]},
    )

    # Verify exam generation and saving
    mock_generate_exam.assert_called_once_with(
        mock_openai_client, mock_cosmos_client, mock_course, mock_llm
    )
    mock_save_and_upload_exam.assert_called_once_with(
        mock_exam, mock_course.id, mock_blob_client
    )

    # Verify course upload to cosmos
    mock_upsert_cosmos.assert_called()


@patch("education_data.workflows.reset_checkpoints_in_cosmos")
@patch("education_data.workflows.reset_concept_profile_in_cosmos")
@patch("education_data.workflows.reset_progress_in_cosmos")
@patch("education_data.workflows.upsert_cosmos")
@patch("education_data.workflows.COURSES")
def test_create_learner(
    mock_courses,
    mock_upsert_cosmos,
    mock_reset_progress,
    mock_reset_concept_profile,
    mock_reset_checkpoints,
    mock_cosmos_client,
    mock_learner,
    mock_course,
):
    # Mock the COURSES data to return the course object
    mock_courses.__getitem__.return_value = mock_course

    create_learner(mock_cosmos_client, mock_learner)

    # Verify learner upload to cosmos
    mock_upsert_cosmos.assert_called_once_with(
        cosmos_client=mock_cosmos_client,
        documents=[mock_learner.model_dump(mode="json")],
        container_name="learners",
    )

    # Verify that reset functions are called for each course
    expected_calls = len(mock_learner.course_ids)
    assert mock_reset_progress.call_count == expected_calls
    assert mock_reset_concept_profile.call_count == expected_calls
    assert mock_reset_checkpoints.call_count == expected_calls

    # Verify the calls are made with correct parameters
    for call in mock_reset_progress.call_args_list:
        args, kwargs = call
        assert kwargs["learner_id"] == mock_learner.id
        assert kwargs["course_id"] in mock_learner.course_ids
        assert kwargs["cosmos_client"] == mock_cosmos_client

    for call in mock_reset_concept_profile.call_args_list:
        args, kwargs = call
        assert kwargs["cosmos_client"] == mock_cosmos_client
        assert kwargs["learner"] == mock_learner

    for call in mock_reset_checkpoints.call_args_list:
        args, kwargs = call
        assert kwargs["learner_id"] == mock_learner.id
        assert kwargs["course_id"] in mock_learner.course_ids
        assert kwargs["cosmos_client"] == mock_cosmos_client


@patch("education_data.workflows.reset_checkpoints_in_cosmos")
@patch("education_data.workflows.reset_progress_in_cosmos")
@patch("education_data.workflows.LEARNER_ID_TO_COURSE_ID")
@patch("education_data.workflows.LEARNERS")
@patch("education_data.workflows.COURSES")
def test_reset_memory(
    mock_courses,
    mock_learners,
    mock_learner_id_to_course_id,
    mock_reset_progress,
    mock_reset_checkpoints,
    mock_cosmos_client,
    mock_course,
    mock_learner,
):
    # Mock the data structures
    mock_courses.__getitem__.return_value = mock_course
    mock_learners.__getitem__.return_value = mock_learner
    mock_learner_id_to_course_id.__getitem__.return_value = [mock_course.id]

    reset_memory(mock_cosmos_client, mock_learner.id, mock_course.id)

    # Verify that reset functions are called
    mock_reset_progress.assert_called_once_with(
        learner_id=mock_learner.id,
        course_id=mock_course.id,
        cosmos_client=mock_cosmos_client,
    )
    mock_reset_checkpoints.assert_called_once_with(
        learner_id=mock_learner.id,
        course_id=mock_course.id,
        cosmos_client=mock_cosmos_client,
    )


@patch("education_data.workflows.reset_checkpoints_in_cosmos")
@patch("education_data.workflows.reset_progress_in_cosmos")
@patch("education_data.workflows.LEARNER_ID_TO_COURSE_ID")
@patch("education_data.workflows.LEARNERS")
@patch("education_data.workflows.COURSES")
def test_reset_memory_learner_not_enrolled(
    mock_courses,
    mock_learners,
    mock_learner_id_to_course_id,
    mock_reset_progress,
    mock_reset_checkpoints,
    mock_cosmos_client,
    mock_course,
    mock_learner,
):
    # Mock the data structures - learner is not enrolled in the course
    mock_courses.__getitem__.return_value = mock_course
    mock_learners.__getitem__.return_value = mock_learner
    # Empty list means not enrolled
    mock_learner_id_to_course_id.__getitem__.return_value = []

    reset_memory(mock_cosmos_client, mock_learner.id, mock_course.id)

    # Verify that reset functions are NOT called when learner is not enrolled
    mock_reset_progress.assert_not_called()
    mock_reset_checkpoints.assert_not_called()

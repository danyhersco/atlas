import pytest
from unittest.mock import AsyncMock, patch, mock_open

from education_data.course.syllabus import (
    generate_syllabus,
)
from education_data.course.syllabus import save_and_upload_syllabus
from models.base import LectureOutline


@pytest.fixture
def mock_course_outline():
    return type(
        "MockCourseOutline",
        (),
        {
            "lectures": [
                LectureOutline(
                    lecture_number=1,
                    title="Lecture 1",
                    sections=["Material 1.1", "Material 1.2"],
                ),
                LectureOutline(
                    lecture_number=2,
                    title="Lecture 2",
                    sections=["Material 2.1", "Material 2.2"],
                ),
            ]
        },
    )()


@pytest.mark.asyncio
async def test_generate_syllabus_output(
    mock_client, mock_course, mock_llm, mock_course_outline
):
    # Mock generate() to return fake outline or lecture content
    with patch(
        "education_data.course.syllabus.generate", new_callable=AsyncMock
    ) as mock_generate:
        # generate will be called once for course outline,
        # then once per lecture
        mock_generate.side_effect = [
            mock_course_outline,  # course outline
            "Lecture 1 content",
            "Lecture 2 content",
        ]

        syllabus = await generate_syllabus(mock_client, mock_course, mock_llm)

        assert "Lecture 1 content" in syllabus
        assert "Lecture 2 content" in syllabus
        assert mock_generate.call_count == 3


@pytest.mark.asyncio
async def test_generate_syllabus_prompt(
    mock_client, mock_course, mock_llm, mock_course_outline
):
    # Mock generate() to return fake outline or lecture content
    with patch(
        "education_data.course.syllabus.generate", new_callable=AsyncMock
    ) as mock_generate:
        # generate will be called once for outline, then once per lecture
        mock_generate.side_effect = [
            mock_course_outline,  # course outline
            "Lecture 1 content",
            "Lecture 2 content",
        ]

        _ = await generate_syllabus(mock_client, mock_course, mock_llm)

        calls = mock_generate.call_args_list

        # Check course outline prompt
        course_outline_prompt = calls[0].kwargs["user_prompt"]
        assert f"Course name: {mock_course.name}" in course_outline_prompt
        assert (
            f"Course description: {mock_course.description}"
            in course_outline_prompt
        )
        assert (
            f"Number of lectures: {mock_course.n_lectures}"
            in course_outline_prompt
        )

        # Check Lecture 1 prompt
        lecture_1_prompt = calls[1].kwargs["user_prompt"]
        assert (
            f"Lecture title: {mock_course_outline.lectures[0].title}"
            in lecture_1_prompt
        )
        assert f"Lecture number: {1}" in lecture_1_prompt
        assert "Previous lectures: " in lecture_1_prompt

        # Check Lecture 2 prompt
        lecture_2_prompt = calls[2].kwargs["user_prompt"]
        assert (
            f"Lecture title: {mock_course_outline.lectures[1].title}"
            in lecture_2_prompt
        )
        assert f"Lecture number: {2}" in lecture_2_prompt
        assert (
            f"Previous lectures: {mock_course_outline.lectures[0].title} "
            f"({', '.join(mock_course_outline.lectures[0].sections)})"
        ) in lecture_2_prompt


@patch("education_data.course.syllabus.BlobServiceClient")
@patch("education_data.course.syllabus.upload_blob")
@patch("builtins.open", new_callable=mock_open)
@patch("os.makedirs")
@patch("education_data.course.syllabus.shutil.rmtree")
def test_save_and_upload_syllabus(
    mock_rmtree,
    mock_makedirs,
    mock_file,
    mock_upload_blob,
    mock_blob_service_client,
    mock_syllabus,
    mock_course,
):
    save_and_upload_syllabus(
        mock_syllabus, mock_course.id, mock_blob_service_client
    )

    mock_makedirs.assert_called_once()

    # The function opens multiple files, so we need to check the call_args_list
    # First call should be the main syllabus file
    file_calls = mock_file.call_args_list
    assert len(file_calls) >= 1  # At least the main syllabus file

    # Check the main syllabus file
    main_file_call = file_calls[0]
    md_path, mode = main_file_call[0]
    assert md_path.name == f"{mock_course.id}.md"
    assert mode == "w"

    # Check that upload_blob was called multiple times
    # First call should be for the main syllabus
    call_args = mock_upload_blob.call_args_list
    assert len(call_args) >= 1

    # Check the first upload_blob call (main syllabus)
    main_syllabus_call = call_args[0]
    _, kwargs = main_syllabus_call
    assert kwargs["blob_service_client"] == mock_blob_service_client
    assert kwargs["container_name"] == "synthetic-data"
    assert kwargs["base_filename"] == f"syllabus_{mock_course.id}.md"
    assert kwargs["local_filepath"].endswith(f"{mock_course.id}.md")

import pytest
from unittest.mock import patch

from education_data.course.exam import generate_exam
from models.base import ExamQuestion


@pytest.mark.asyncio
@patch("education_data.course.exam.retrieve_concept_tool")
@patch("education_data.course.exam.generate")
@patch("education_data.course.exam.get_cosmos_docs_with_ids")
async def test_generate_exam_output(
    mock_get_cosmos_docs,
    mock_generate,
    mock_retrieve_concept_tool,
    mock_client,
    mock_cosmos_client,
    mock_course,
    mock_llm,
    mock_exam,
):
    # Mock the cosmos response to return concept IDs
    mock_get_cosmos_docs.return_value = [{"concept_ids": ["concept1"]}]
    # Mock the concept retrieval to return fake content
    mock_retrieve_concept_tool.return_value = "Fake concept content"
    mock_generate.return_value = mock_exam[0]  # Return single ExamQuestion

    exam = await generate_exam(
        mock_client, mock_cosmos_client, mock_course, mock_llm
    )

    mock_generate.assert_called_once()

    assert len(exam) == 1  # one question
    assert isinstance(exam[0], ExamQuestion)
    assert exam[0].question == "What is 2 + 2?"
    assert all(
        choice in exam[0].choices
        for choice in ["A. 3", "B. 4", "C. 5", "D. 6", "E. 7"]
    )


@pytest.mark.asyncio
@patch("education_data.course.exam.retrieve_concept_tool")
@patch("education_data.course.exam.generate")
@patch("education_data.course.exam.get_cosmos_docs_with_ids")
async def test_generate_exam_prompt(
    mock_get_cosmos_docs,
    mock_generate,
    mock_retrieve_concept_tool,
    mock_client,
    mock_cosmos_client,
    mock_course,
    mock_llm,
    mock_exam,
):
    # Mock the cosmos response to return concept IDs
    mock_get_cosmos_docs.return_value = [{"concept_ids": ["concept1"]}]
    # Mock the concept retrieval to return fake content
    mock_retrieve_concept_tool.return_value = "Fake concept content"
    mock_generate.return_value = mock_exam[0]  # Return single ExamQuestion

    _ = await generate_exam(
        mock_client, mock_cosmos_client, mock_course, mock_llm
    )

    mock_generate.assert_called_once()

    call = mock_generate.call_args_list[0]
    user_prompt = call.kwargs["user_prompt"]

    assert f"Course name: {mock_course.name}" in user_prompt
    assert "Fake concept content" in user_prompt

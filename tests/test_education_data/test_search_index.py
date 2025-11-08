import pytest
from unittest.mock import MagicMock, patch

from education_data.course.search_index import (
    chunk_syllabus,
    create_embedding,
    create_search_index,
    add_chunks_to_index,
    make_syllabus_search_index,
)
from models.base import EmbeddedSection


DUMMY_MD = """
# Lecture 1: Introduction to Physics
## Section 1.1: What is Physics?
Physics is the study of matter and energy.

# Lecture 2: Classical Mechanics
## Section 2.1: Newton's Laws
Newton's laws explain motion.
"""


@pytest.fixture
def dummy_chunks():
    return chunk_syllabus(DUMMY_MD, by="section")


def test_chunk_syllabus(dummy_chunks):
    assert len(dummy_chunks) == 2

    assert dummy_chunks[0].lecture_number == 1
    assert dummy_chunks[0].lecture_title == "Introduction to Physics"
    assert dummy_chunks[0].section_number == 1
    assert dummy_chunks[0].section_title == "Section 1.1: What is Physics?"
    assert (
        dummy_chunks[0].content == "Physics is the study of matter and energy."
    )

    assert dummy_chunks[1].lecture_number == 2
    assert dummy_chunks[1].lecture_title == "Classical Mechanics"
    assert dummy_chunks[1].section_number == 1
    assert dummy_chunks[1].section_title == "Section 2.1: Newton's Laws"
    assert dummy_chunks[1].content == "Newton's laws explain motion."


@patch("education_data.course.search_index.AzureOpenAI")
def test_create_embedding(mock_aoai, dummy_chunks):
    mock_client = mock_aoai()
    mock_client.embeddings.create.return_value.data = [
        MagicMock(embedding=[0.1] * 3072) for _ in dummy_chunks
    ]

    embeddings = create_embedding(
        mock_client, dummy_chunks, model="dummy-model"
    )
    assert len(embeddings) == len(dummy_chunks)
    assert isinstance(embeddings[0], EmbeddedSection)


@patch("education_data.course.search_index.get_search_index_client")
@patch("education_data.course.search_index.get_env_var")
def test_create_vector_index(mock_get_env_var, mock_get_search_index_client):
    mock_get_env_var.side_effect = lambda key: (
        "dummy-endpoint" if "ENDPOINT" in key else "dummy-key"
    )
    mock_client = MagicMock()
    mock_client.list_index_names.return_value = ["existing-index"]
    mock_get_search_index_client.return_value = mock_client

    create_search_index("existing-index")
    mock_client.delete_index.assert_called_once_with("existing-index")
    mock_client.create_index.assert_called_once()


@patch("education_data.course.search_index.SearchClient")
@patch("education_data.course.search_index.get_env_var")
def test_add_chunks_index(
    mock_get_env_var, mock_search_client_cls, dummy_chunks
):
    mock_get_env_var.side_effect = lambda key: (
        "dummy-endpoint" if "ENDPOINT" in key else "dummy-key"
    )
    mock_client = MagicMock()
    mock_client.upload_documents.return_value = [
        MagicMock(succeeded=True) for _ in dummy_chunks
    ]
    mock_search_client_cls.return_value = mock_client

    embedded = [
        EmbeddedSection(**chunk.model_dump(), embedding=[0.1] * 3072)
        for chunk in dummy_chunks
    ]
    add_chunks_to_index("dummy-index", embedded)
    assert mock_client.upload_documents.called
    assert (
        mock_client.upload_documents.call_args[1]["documents"][0]["embedding"]
        == [0.1] * 3072
    )


@patch("education_data.course.search_index.get_env_var")
@patch("education_data.course.search_index.chunk_syllabus")
@patch("education_data.course.search_index.create_embedding")
@patch("education_data.course.search_index.create_search_index")
@patch("education_data.course.search_index.add_chunks_to_index")
def test_make_syllabus_vector_index(
    mock_add_chunks_to_index,
    mock_create_vector_index,
    mock_create_embedding,
    mock_chunk_syllabus,
    mock_get_env_var,
    mock_syllabus,
):
    mock_get_env_var.side_effect = lambda key: (
        "dummy-endpoint" if "ENDPOINT" in key else "dummy-key"
    )
    make_syllabus_search_index(mock_syllabus, "test-index")

    mock_chunk_syllabus.assert_called_once_with(mock_syllabus, by="section")
    mock_create_embedding.assert_called_once()
    mock_create_vector_index.assert_called_once_with("test-index")
    mock_add_chunks_to_index.assert_called_once()

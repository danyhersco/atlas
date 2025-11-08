import pytest
from unittest.mock import patch, mock_open

from education_data.course.roadmap import (
    save_and_upload_roadmap,
    generate_roadmap,
    group_sections,
)
from models.base import CourseRoadmap, Concept, CourseID, Section


@pytest.fixture
def mock_course_roadmap():
    return CourseRoadmap(
        id="rm-MAT901",
        course_id=CourseID.MAT901,
        concepts=[
            Concept(
                id="introduction-to-mathematics",
                course_id=CourseID.MAT901,
                lecture_number=1,
                section_number=1,
                title="Introduction to Mathematics",
                description="Basic concepts and foundations",
                goal="Understand fundamental mathematical principles",
                exercises=["1.1", "1.2"],
            ),
            Concept(
                id="algebraic-operations",
                course_id=CourseID.MAT901,
                lecture_number=1,
                section_number=2,
                title="Algebraic Operations",
                description="Basic algebraic manipulations",
                goal="Master basic algebraic operations",
                exercises=["1.3", "1.4"],
            ),
        ],
    )


@pytest.fixture
def mock_sections():
    return [
        Section(
            id="lecture-1-section-1",
            lecture_number=1,
            lecture_title="Introduction",
            section_number=1,
            section_title="Basic Concepts",
            content="Introduction to basic mathematical concepts...",
        ),
        Section(
            id="lecture-1-section-2",
            lecture_number=1,
            lecture_title="Introduction",
            section_number=2,
            section_title="Exercise 1.1",
            content="Practice problems for basic concepts...",
        ),
        Section(
            id="lecture-2-section-1",
            lecture_number=2,
            lecture_title="Advanced Topics",
            section_number=1,
            section_title="Complex Numbers",
            content="Introduction to complex numbers...",
        ),
        Section(
            id="lecture-2-section-2",
            lecture_number=2,
            lecture_title="Advanced Topics",
            section_number=2,
            section_title="Exercise 2.1",
            content="Practice problems for complex numbers...",
        ),
    ]


@patch("education_data.course.roadmap.upsert_cosmos")
@patch("education_data.course.roadmap.delete_cosmos_with_fields")
def test_save_and_upload_roadmap(
    mock_delete_cosmos,
    mock_upsert_cosmos,
    mock_cosmos_client,
    mock_course_roadmap,
):
    """Test the save_and_upload_roadmap function."""

    save_and_upload_roadmap(mock_cosmos_client, mock_course_roadmap)

    # Verify that existing concepts are deleted
    mock_delete_cosmos.assert_called_once_with(
        cosmos_client=mock_cosmos_client,
        container_name="concepts",
        fields={"course_id": mock_course_roadmap.course_id},
    )

    # Verify that upsert_cosmos is called twice:
    # 1. For the roadmap document
    # 2. For all the concepts
    assert mock_upsert_cosmos.call_count == 2

    # Check the first call (roadmap)
    roadmap_call = mock_upsert_cosmos.call_args_list[0]
    args, kwargs = roadmap_call
    assert kwargs["cosmos_client"] == mock_cosmos_client
    assert kwargs["container_name"] == "roadmaps"
    assert len(kwargs["documents"]) == 1

    roadmap_doc = kwargs["documents"][0]
    assert roadmap_doc["id"] == mock_course_roadmap.id
    assert roadmap_doc["course_id"] == mock_course_roadmap.course_id
    assert roadmap_doc["concept_ids"] == [
        "introduction-to-mathematics",
        "algebraic-operations",
    ]

    # Check the second call (concepts)
    concepts_call = mock_upsert_cosmos.call_args_list[1]
    args, kwargs = concepts_call
    assert kwargs["cosmos_client"] == mock_cosmos_client
    assert kwargs["container_name"] == "concepts"
    assert len(kwargs["documents"]) == 2  # Two concepts


@patch("education_data.course.roadmap.generate")
@patch("education_data.course.roadmap.chunk_syllabus")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        "# Lecture 1: Introduction\n\n## 1.1 Basic Concepts\n\nContent here..."
    ),
)
@patch("pathlib.Path.exists")
@pytest.mark.asyncio
async def test_generate_roadmap(
    mock_path_exists,
    mock_file,
    mock_chunk_syllabus,
    mock_generate,
    mock_client,
    mock_course,
    mock_llm,
    mock_sections,
):
    """Test the generate_roadmap function."""

    # Mock the path exists check
    mock_path_exists.return_value = True

    # Mock the chunk_syllabus function
    mock_chunk_syllabus.return_value = mock_sections

    # Mock the LLM response for concept generation
    mock_concept_output = type(
        "MockConceptOutput",
        (),
        {
            "concepts": [
                type(
                    "MockConcept",
                    (),
                    {
                        "lecture_number": 1,
                        "section_number": 1,
                        "title": "Introduction to Mathematics",
                        "description": "Basic concepts and foundations",
                        "goal": (
                            "Understand fundamental mathematical principles"
                        ),
                        "exercises": ["1.1", "1.2"],
                    },
                )(),
                type(
                    "MockConcept",
                    (),
                    {
                        "lecture_number": 2,
                        "section_number": 1,
                        "title": "Complex Numbers",
                        "description": "Introduction to complex numbers",
                        "goal": "Master complex number operations",
                        "exercises": ["2.1"],
                    },
                )(),
            ]
        },
    )()

    mock_generate.return_value = mock_concept_output

    # Call the function
    result = await generate_roadmap(mock_client, mock_course, mock_llm)

    # Verify the result
    assert isinstance(result, CourseRoadmap)
    assert result.id == f"rm-{mock_course.id}"
    assert result.course_id == mock_course.id

    # The function processes 2 section groups,
    # so we expect 2 concepts per group = 4 total
    assert len(result.concepts) == 4

    # Check first concept
    concept1 = result.concepts[0]
    assert concept1.id == "introduction-to-mathematics"
    assert concept1.title == "Introduction to Mathematics"
    assert concept1.description == "Basic concepts and foundations"
    assert concept1.goal == "Understand fundamental mathematical principles"
    assert concept1.exercises == ["1.1", "1.2"]

    # Check second concept
    concept2 = result.concepts[1]
    assert concept2.id == "complex-numbers"
    assert concept2.title == "Complex Numbers"
    assert concept2.description == "Introduction to complex numbers"
    assert concept2.goal == "Master complex number operations"
    assert concept2.exercises == ["2.1"]

    # Verify that chunk_syllabus was called
    mock_chunk_syllabus.assert_called_once_with(
        (
            "# Lecture 1: Introduction\n\n## 1.1 Basic "
            "Concepts\n\nContent here..."
        ),
        by="section",
    )

    # Verify that generate was called (for concept generation)
    mock_generate.assert_called()


@patch("education_data.course.roadmap.generate")
@patch("education_data.course.roadmap.chunk_syllabus")
@patch(
    "builtins.open",
    new_callable=mock_open,
    read_data=(
        "# Lecture 1: Introduction\n\n## 1.1 Basic Concepts\n\nContent here..."
    ),
)
@patch("pathlib.Path.exists")
@pytest.mark.asyncio
async def test_generate_roadmap_file_not_found(
    mock_path_exists,
    mock_file,
    mock_chunk_syllabus,
    mock_generate,
    mock_client,
    mock_course,
    mock_llm,
):
    """Test the generate_roadmap function when syllabus file doesn't exist."""

    # Mock the path exists check to return False
    mock_path_exists.return_value = False

    # The function should raise FileNotFoundError
    with pytest.raises(FileNotFoundError) as exc_info:
        await generate_roadmap(mock_client, mock_course, mock_llm)

    # The error message includes the full path, so we check for the course ID
    assert str(mock_course.id) in str(exc_info.value)


@pytest.mark.asyncio
async def test_group_sections(mock_sections):
    """Test the group_sections function."""

    result = await group_sections(mock_sections)

    # Should create 2 groups based on the mock sections
    assert len(result) == 2

    # First group: Lecture 1 sections
    first_group = result[0]
    assert len(first_group) == 2
    assert first_group[0].lecture_number == 1
    assert first_group[0].section_number == 1
    assert first_group[0].section_title == "Basic Concepts"
    assert first_group[1].lecture_number == 1
    assert first_group[1].section_number == 2
    assert first_group[1].section_title == "Exercise 1.1"

    # Second group: Lecture 2 sections
    second_group = result[1]
    assert len(second_group) == 2
    assert second_group[0].lecture_number == 2
    assert second_group[0].section_number == 1
    assert second_group[0].section_title == "Complex Numbers"
    assert second_group[1].lecture_number == 2
    assert second_group[1].section_number == 2
    assert second_group[1].section_title == "Exercise 2.1"


@pytest.mark.asyncio
async def test_group_sections_empty_list():
    """Test group_sections with an empty list."""

    result = await group_sections([])
    assert result == []


@pytest.mark.asyncio
async def test_group_sections_single_section():
    """Test group_sections with a single section."""

    single_section = [
        Section(
            id="lecture-1-section-1",
            lecture_number=1,
            lecture_title="Introduction",
            section_number=1,
            section_title="Basic Concepts",
            content="Introduction to basic mathematical concepts...",
        )
    ]

    result = await group_sections(single_section)
    assert len(result) == 1
    assert len(result[0]) == 1
    assert result[0][0].section_title == "Basic Concepts"

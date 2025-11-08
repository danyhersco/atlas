# ruff: noqa: E501

from typing import Annotated, Literal
from pydantic import Field

from fastmcp import FastMCP

from model_context_protocol.functions import (
    retrieve_course_content_tool,
    retrieve_learner_progress_tool,
    switch_concept_tool,
    update_learner_preferences_tool,
)
from utils.logger_config import logger


mcp = FastMCP(
    name="matlas",
    instructions="""
This server provides tools to interact with a university course. Here are the available tools:
- retrieve_course_content: Retrieve content from the course syllabus.
- retrieve_learner_progress: Retrieve the progress of a specific learner in a specific course. Progress includes a list of concepts along with the progression status, and other practical information.
- switch_concept: Switch the current concept to a new one, updating the status and evidence accordingly.
- updated_learner_preferences: Update the learning preferences of a learner.
""",
)


@mcp.tool()
def retrieve_course_content(
    query: Annotated[
        str,
        Field(
            description="The query you would like to base the retrieval of information. It will be compared to chunks of the syllabus."
        ),
    ],
    course_id: Annotated[
        Literal["PYT101", "ECO901", "MAT901", "LAW901", "FIN901"],
        Field(
            description="The course code of the course you'd like to retrieve information from."
        ),
    ],
) -> str:
    """
    Retrieves content from the course syllabus.
    It is useful as the content of the syllabus is the exact material the student need to master to maximise their academic results.
    It should be mostly used when a student asks about a specific topic, concept, or question related to the course, but not to the current concept you are making a student master.
    Use it whenever you need further context about the course content.

    Parameters:
        query: The search query you would like to retrieval of information from. It will be compared to chunks of the syllabus, and the most relevant chunks will be returned.
        course_id: The course code of the course you'd like to retrieve information from. Can be either one of the following: PYT101, ECO901, MAT901, LAW901, FIN901.

    Returns:
        A string, representing a concatenation of all retrieved snippets from the syllabus, relevant to the query.
    """
    logger.debug(
        "Using retrieve_course_content with:\n"
        f"course_id={course_id}\nquery={query}"
    )
    return retrieve_course_content_tool(query, course_id)


@mcp.tool(enabled=False)  # Disabled for now as it does not work well
def retrieve_learner_progress(
    learner_id: Annotated[
        Literal[
            "learner_1",
            "learner_2",
            "learner_3",
            "learner_4",
            "learner_5",
            "learner_6",
            "learner_7",
            "learner_8",
            "learner_9",
            "learner_10",
        ],
        Field(
            description="The ID of the learner whose progress you want to retrieve."
        ),
    ],
    course_id: Annotated[
        Literal["PYT101", "ECO901", "MAT901", "LAW901", "FIN901"],
        Field(
            description="The course ID for which you want to retrieve the learner's progress."
        ),
    ],
) -> str:
    """
    Retrieves the progress of a specific learner in a specific course.
    This is formatted as a list of concepts, along with the progression status, and other practical information.
    This can be useful to understand how much progress a learner has made in a course, which concepts they have mastered, which ones they still need to work on, and those that are still in progress.

    Parameters:
        learner_id: The ID of the learner whose progress you want to retrieve.
        course_id: The ID of the course for which you want to retrieve the learner's progress. Can be either one of the following: PYT101, ECO901, MAT901, LAW901, FIN901.

    Returns:
        A string representing the learner's progress in the specified course.
    """
    logger.debug(
        "Using retrieve_learner_progress_tool with:\n"
        f"learner_id={learner_id}\ncourse_id={course_id}"
    )
    return retrieve_learner_progress_tool(learner_id, course_id)


@mcp.tool()
def switch_concept(
    current_concept_id: Annotated[
        str,
        Field(description="The ID of the current concept."),
    ],
    current_concept_status: Annotated[
        Literal["mastered", "confused"],
        Field(description="The status of the current concept."),
    ],
    current_concept_evidence: Annotated[
        str,
        Field(description="Evidence for the current concept's status."),
    ],
    next_concept_id: Annotated[
        str,
        Field(description="The ID of the next concept to switch to."),
    ],
    learner_id: Annotated[
        Literal[
            "learner_1",
            "learner_2",
            "learner_3",
            "learner_4",
            "learner_5",
            "learner_6",
            "learner_7",
            "learner_8",
            "learner_9",
            "learner_10",
        ],
        Field(description="The ID of the learner."),
    ],
    course_id: Annotated[
        Literal["PYT101", "ECO901", "MAT901", "LAW901", "FIN901"],
        Field(description="The ID of the course."),
    ],
) -> str:
    """
    Switches the current concept to a new one, updating the status and evidence accordingly.
    You should use this tool when you conclude that the learner has mastered the current concept or if it is a confusion for them.
    This tool, makes changes the concept in progress as eiter mastered or confused, and switches to the next concept in progress.
    It also retrieves the next concept information including its title, description, criterion for mastery, learnable content, and exercises.

    Parameters:
        current_concept_id: The ID of the concept in progress.
        current_concept_status: The status of the current concept.
        current_concept_evidence: Evidence for the current concept's status.
        next_concept_id: The ID of the next concept to switch to.
        learner_id: The ID of the learner.
        course_id: The ID of the course.

    Returns:
        Everything you need to know about the next concept.
    """
    logger.debug(
        f"Using switch_concept with:\n"
        f"current_concept_id={current_concept_id}\n"
        f"current_concept_status={current_concept_status}\n"
        f"current_concept_evidence={current_concept_evidence}\n"
        f"next_concept_id={next_concept_id}\n"
        f"learner_id={learner_id}\n"
        f"course_id={course_id}"
    )
    return switch_concept_tool(
        current_concept_id,
        current_concept_status,
        current_concept_evidence,
        next_concept_id,
        learner_id,
        course_id,
    )


@mcp.tool()
def update_learner_preferences(
    learner_id: Annotated[
        Literal[
            "learner_1",
            "learner_2",
            "learner_3",
            "learner_4",
            "learner_5",
            "learner_6",
            "learner_7",
            "learner_8",
            "learner_9",
            "learner_10",
        ],
        Field(
            description="The ID of the learner whose preferences you want to update."
        ),
    ],
    course_id: Annotated[
        Literal["PYT101", "ECO901", "MAT901", "LAW901", "FIN901"],
        Field(
            description="The ID of the course for which you want to update the learner's preferences."
        ),
    ],
    new_preferences: Annotated[
        list[str],
        Field(
            description="A list of new learning preferences for the learner."
        ),
    ],
) -> str:
    """
    Updates the learning preferences of a learner, which is a list of strings.
    This can be useful to tailor the learning experience to the specific needs and preferences of the learner.
    The current preferences are already provided in the learner's profile. By providing new preferences you can:
        - Keep the preferences that you want to keep
        - Update the ones you want to change
        - Add new ones
        - Delete the ones you want to delete

    Parameters:
        learner_id: The ID of the learner whose preferences you want to update.
        course_id: The ID of the course for which you want to update the learner's preferences. Can be either one of the following: PYT101, ECO901, MAT901, LAW901, FIN901.
        new_preferences: A list of new learning preferences for the learner.

    Returns:
        A message indicating the result of the update operation.
    """
    logger.debug(
        f"Using updated_learner_preferences with:\n"
        f"learner_id={learner_id}\ncourse_id={course_id}\n"
        f"new_preferences={new_preferences}"
    )
    return update_learner_preferences_tool(
        learner_id=learner_id,
        course_id=course_id,
        new_preferences=new_preferences,
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")

from typing import Literal
from datetime import datetime

from azure.search.documents.models import (
    QueryType,
    QueryCaptionType,
    QueryAnswerType,
    VectorizableTextQuery,
)
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

from models.base import (
    BlobContainer,
    CosmosContainer,
    Section,
)
from utils.clients import get_blob_service_client, get_cosmos_client
from utils.get_env_var import get_env_var
from utils.logger_config import logger
from utils.azure_storage_utils import (
    get_blob,
    get_cosmos_docs_with_ids,
    get_cosmos_docs_with_fields,
)


def retrieve_course_content_tool(
    query: str,
    course_id: str,
) -> str:
    """
    Retrieves relevant course content sections based on a query using
    Azure AI Search.

    This method performs a hybrid search on the course's search index,
    then passing through a semantic reranker, the function returns the
    top matching sections as formatted strings. Hybrid search means
    both keyword and embedding-based search to find the most
    relevant content.

    Args:
        query (str): The search query or question.
        course_id (str): The ID of the course to search within.

    Returns:
        str: A concatenated string of the top matching Section objects,
            separated by newlines.
    """
    index_name = course_id.lower()

    search_client = SearchClient(
        get_env_var("AZURE_SEARCH_ENDPOINT"),
        index_name,
        AzureKeyCredential(get_env_var("AZURE_SEARCH_KEY")),
    )
    # wrap the query in a Azure AI Search compatible format
    vector_query = VectorizableTextQuery(
        text=query,
        k_nearest_neighbors=10,
        fields="embedding",
    )
    # perform search query in search index
    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        query_type=QueryType.SEMANTIC,
        semantic_configuration_name="semantic_config",
        query_caption=QueryCaptionType.EXTRACTIVE,
        query_answer=QueryAnswerType.EXTRACTIVE,
        top=3,  # keep top three results
    )

    # build section from results
    documents = [
        Section(
            id=result["id"],
            lecture_number=result["lecture_number"],
            lecture_title=result["lecture_title"],
            section_number=result["section_number"],
            section_title=result["section_title"],
            content=result["content"],
        )
        for result in results
    ]

    # return a formatted string
    return "\n\n\n".join(str(doc) for doc in documents)


def retrieve_learner_progress_tool(
    learner_id: str,
    course_id: str,
) -> str:
    """
    Retrieves the progress status of all concepts for a learner
    in a given course.

    This method queries Cosmos DB for progress documents matching
    the learner and course, then summarises the concepts by their
    status: mastered, in progress, not started, and confused.

    Args:
        learner_id (str): The ID of the learner.
        course_id (str): The ID of the course.

    Returns:
        str: A formatted string listing mastered, in progress,
            not started, and confused concepts. This represents
            the learner progress!
    """

    cosmos_client = get_cosmos_client()
    # retrieve all progress entries for learner_id
    # in course_id
    progress_docs = get_cosmos_docs_with_fields(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.PROGRESSES,
        fields={
            "course_id": course_id,
            "learner_id": learner_id,
        },
    )
    # group concepts by status
    lines = [
        "Mastered concepts: "
        + ", ".join(
            doc["concept_id"]
            for doc in progress_docs
            if doc["status"] == "mastered"
        ),
        "In progress concept: "
        + ", ".join(
            doc["concept_id"]
            for doc in progress_docs
            if doc["status"] == "in_progress"
        ),
        "Not started concepts: "
        + ", ".join(
            doc["concept_id"]
            for doc in progress_docs
            if doc["status"] == "not_started"
        ),
        "Confusion concepts (come back later): "
        + ", ".join(
            doc["concept_id"]
            for doc in progress_docs
            if doc["status"] == "confused"
        ),
    ]
    progress = "\n".join(lines)  # format progress as string
    return progress


def retrieve_concept_tool(concept_id: str) -> str:
    """
    Retrieves detailed information and content for a specific concept.

    This method queries Cosmos DB for the concept metadata, loads the
    learnable content and associated exercises from Azure Blob Storage,
    and formats all information into a readable string.

    Args:
        concept_id (str): The ID of the concept to retrieve.

    Returns:
        str: A formatted string containing the concept's ID, title,
            description, goal, learnable content, and exercises.
    """
    cosmos_client = get_cosmos_client()

    # get concept object, already containing meaningful info
    concept = get_cosmos_docs_with_ids(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.CONCEPTS,
        document_ids=[concept_id],
    )[0]

    # retrieve the learnable section associated to the concept
    # from Azure Blob Storage
    blob_service_client = get_blob_service_client()
    learnable_content = get_blob(
        blob_service_client=blob_service_client,
        container_name=BlobContainer.SYNTHETIC_DATA,
        blob_name=(
            f"{concept['course_id']}/lecture-{concept['lecture_number']}"
            f"-section-{concept['section_number']}.md"
        ),
    )

    # retrieve the exercises associated to the concept from
    # Azure Blob Storage
    exercises = []
    for ex_number in concept["exercises"]:
        exercises.append(
            get_blob(
                blob_service_client=blob_service_client,
                container_name=BlobContainer.SYNTHETIC_DATA,
                blob_name=(f"{concept['course_id']}/exercise-{ex_number}.md"),
            )
        )

    # format everything together in a nice string
    concept_formatted = (
        f"Concept ID: {concept['id']}\n"
        f"Concept Title: {concept['title']}\n"
        f"Concept Description: {concept['description']}\n"
        f"Concept Goal: {concept['goal']}\n\n"
        f"Learnable Content:\n\n{learnable_content}\n\n"
        f"Exercises:\n\n{'\n\n'.join(exercises)}"
    )
    logger.info(f"Retrieved concept_id={concept_id}.")
    return concept_formatted


def update_concept_status_tool(
    concept_id: str,
    status: Literal["not_started", "in_progress", "mastered", "confused"],
    evidence: str,
    learner_id: str,
    course_id: str,
) -> str:
    """
    Updates the progress status of a concept for a learner in a given course.

    This method finds the progress entry for the specified learner, course,
    and concept in Cosmos DB, updates its status (with evidence) and saves
    the changes back to the database.

    Args:
        concept_id (str): The ID of the concept to update.
        status (Literal): The new status for the concept
            ("not_started", "in_progress", "mastered", "confused").
        evidence (str): Evidence or reasoning for the status update.
        learner_id (str): The ID of the learner.
        course_id (str): The ID of the course.

    Returns:
        str: A confirmation message indicating the concept was updated.

    Raises:
        ValueError: If zero or multiple progress entries are found for
            the specified learner, course, and concept.
    """
    cosmos_client = get_cosmos_client()

    # get progress entry for learner_id in concept_id from course_id
    documents = get_cosmos_docs_with_fields(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.PROGRESSES,
        fields={
            "learner_id": learner_id,
            "course_id": course_id,
            "concept_id": concept_id,
        },
    )

    if len(documents) == 0 or len(documents) > 1:  # safety checks
        raise ValueError(
            "Zero or multiple progress entries found for learner "
            f"{learner_id}, course {course_id}, concept {concept_id}."
        )

    concept_progress = documents[0]  # there must be only one
    # update status with evidence
    concept_progress["status"] = status
    concept_progress["evidence"] = evidence
    concept_progress["last_updated"] = str(datetime.now())

    # update progress entry in Cosmos DB
    database = cosmos_client.get_database_client("campus")
    progresses_container = database.get_container_client(
        CosmosContainer.PROGRESSES
    )

    progresses_container.replace_item(
        item=concept_progress["id"], body=concept_progress
    )

    return (
        f"Updated concept {concept_id} successfully to "
        f"status '{status}' with evidence '{evidence}'."
    )


def switch_concept_tool(
    current_concept_id: str,
    current_concept_status: Literal[
        "not_started", "in_progress", "mastered", "confused"
    ],
    current_concept_evidence: str,
    next_concept_id: str,
    learner_id: str,
    course_id: str,
) -> str:
    """
    Updates the status of the current concept and switches
    the focus to a new concept.

    This method first updates the status and evidence for the
    current concept in Cosmos DB, then marks the next concept
    as "in_progress" for the learner. It retrieves and returns
    the formatted details of the next concept.

    Args:
        current_concept_id (str): The ID of the current concept.
        current_concept_status (Literal): The new status for
            the current concept.
        current_concept_evidence (str): Evidence or reasoning
            for the status update.
        next_concept_id (str): The ID of the next concept to switch to.
        learner_id (str): The ID of the learner.
        course_id (str): The ID of the course.

    Returns:
        str: A formatted string containing the details of the next concept.
    """
    message = update_concept_status_tool(
        concept_id=current_concept_id,
        status=current_concept_status,
        evidence=current_concept_evidence,
        learner_id=learner_id,
        course_id=course_id,
    )
    logger.info(message)
    message = update_concept_status_tool(
        concept_id=next_concept_id,
        status="in_progress",
        evidence="Learner is currently mastering this concept.",
        learner_id=learner_id,
        course_id=course_id,
    )
    logger.info(message)
    next_concept_formatted = retrieve_concept_tool(next_concept_id)
    logger.info(
        f"Concept {current_concept_id} marked as {current_concept_status}, "
        f"switching to concept {next_concept_id} for learner {learner_id} in "
        f"course {course_id}."
    )
    return next_concept_formatted


def update_learner_preferences_tool(
    learner_id: str,
    course_id: str,
    new_preferences: list[str],
) -> str:
    """
    Updates the learning preferences for a learner in a specific course.

    This method retrieves the learner's document from Cosmos DB, updates the
    learning preferences for the given course, and saves the changes back to
    the database.

    Args:
        learner_id (str): The ID of the learner.
        course_id (str): The ID of the course.
        new_preferences (list[str]): The new list of learning preferences.

    Returns:
        str: A confirmation message indicating the preferences were updated.
    """

    cosmos_client = get_cosmos_client()

    # retrieve learner documents, which includes preferences
    document = get_cosmos_docs_with_ids(
        cosmos_client=cosmos_client,
        container_name=CosmosContainer.LEARNERS,
        document_ids=[learner_id],
    )[0]

    # update the preferences list
    document["learning_preferences"][course_id] = new_preferences

    # save changes to Cosmos DB
    database = cosmos_client.get_database_client("campus")
    learners_container = database.get_container_client(
        CosmosContainer.LEARNERS
    )

    learners_container.replace_item(item=document["id"], body=document)

    return (
        f"Updated learning preferences for learner {learner_id} "
        f"in course {course_id}."
    )

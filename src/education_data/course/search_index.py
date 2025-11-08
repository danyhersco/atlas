import re
from typing import Literal

from openai import AzureOpenAI

from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    SearchFieldDataType,
    HnswAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    SearchField,
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters,
)
from azure.core.credentials import AzureKeyCredential

from utils.clients import get_search_index_client
from utils.logger_config import logger
from utils.get_env_var import get_env_var
from models.base import Section, EmbeddedSection, Lecture


def chunk_syllabus(
    markdown_text: str, by: Literal["section", "lecture"] = "section"
) -> list[Section] | list[Lecture]:
    """
    Splits the syllabus markdown text into chunks, either by
    section or lecture.

    A syllabus is made lectures, themselves made of sections.
    markdown_text represents the syllabus in markdown format.

    Note: this function does not offer much flexibility and requires
    a very specific markdown course structure. Future work considers
    generalizing this function to handle a wider variety of syllabus formats.
    """
    logger.debug(f"Chunking syllabus by {by}...")
    chunks = []

    # Split text by top-level lectures, which started with `# Lecture`
    lecture_blocks = re.split(
        r"(?=^# Lecture \d+)", markdown_text, flags=re.MULTILINE
    )

    for lecture_block in lecture_blocks:
        lecture_block = lecture_block.strip()
        if not lecture_block:
            logger.warning("Empty lecture block found, skipping...")
            continue

        # extract lecture number and title
        lecture_header_match = re.match(
            r"# Lecture (\d+):?\s*(.*)", lecture_block
        )
        if not lecture_header_match:
            logger.warning(
                "Lecture header not found or malformed, skipping lecture..."
            )
            continue

        lecture_number = lecture_header_match.group(1)
        lecture_title = lecture_header_match.group(2).strip()

        # remove the lecture header to isolate section content
        section_text = lecture_block[
            len(lecture_header_match.group(0)) :
        ].strip()

        if by == "lecture":
            chunks.append(
                Lecture(
                    id=f"lecture-{lecture_number}",
                    number=int(lecture_number),
                    title=lecture_title,
                    content=section_text,
                )
            )
            continue  # skip section splitting

        # split lectures into sections using ## headers
        section_blocks = re.split(
            r"(?=^## .+)", section_text, flags=re.MULTILINE
        )
        section_number = 0

        # form Section object for each raw section block
        for section_block in section_blocks:
            section_block = section_block.strip()
            if not section_block.startswith("## "):
                logger.warning(
                    "Section block does not start with '##', skipping. "
                    f"Section content: {section_block[:50]}..."
                )
                continue

            section_number += 1
            lines = section_block.splitlines()  # to separate title to content
            section_title = lines[0].replace("##", "").strip()
            content = "\n".join(lines[1:]).strip()

            syllabus_chunk = Section(
                id=f"lecture-{lecture_number}-section-{section_number}",
                lecture_number=int(lecture_number),
                lecture_title=lecture_title,
                section_number=section_number,
                section_title=section_title,
                content=content,
            )
            chunks.append(syllabus_chunk)

    logger.debug(f"Successfully chunked syllabus by {by}...")

    return chunks


def create_embedding(
    client: AzureOpenAI,
    syllabus_chunks: list[Section],
    model: str = "text-embedding-3-large",
) -> list[EmbeddedSection]:
    """
    Takes a list of syllabus sections and creates vector embeddings
    for each section. The function returns a list of Section object,
    with `embedding` field added, which we call `EmbeddedSection`.

    Default model is OpenAI's text-embedding-3-large. If you have other
    models you would like to use, you need to deploy them in your Azure
    Foundry account and input the deployment name here.
    """

    # create document strings for each syllabus chunk,
    # which will be used for embedding
    documents = [
        (
            f"Lecture: {chunk.lecture_title}\n"
            f"Section: {chunk.section_title}\n"
            f"Content: {chunk.content}"
        )
        for chunk in syllabus_chunks
    ]

    logger.debug("Creating embeddings for syllabus chunks...")

    # call OpenAI's embeddings API to generate embeddings
    response = client.embeddings.create(
        input=documents,
        model=model,
    )

    embeddings = response.data  # where the list of embeddings is stored
    if len(embeddings) != len(syllabus_chunks):  # safety check
        raise ValueError(
            "Number of embeddings does not match number of syllabus chunks."
        )

    embedded_chunks = []
    # add embedding to each existing section
    for chunk, embedding in zip(syllabus_chunks, embeddings):
        embedded_chunk = EmbeddedSection(
            id=chunk.id,
            lecture_number=chunk.lecture_number,
            lecture_title=chunk.lecture_title,
            section_number=chunk.section_number,
            section_title=chunk.section_title,
            content=chunk.content,
            embedding=embedding.embedding,
        )
        embedded_chunks.append(embedded_chunk)
        logger.debug(f"Created embedding for chunk: {chunk.id}")

    return embedded_chunks


def create_search_index(index_name: str) -> None:
    """
    Creates a search index in Azure AI Search, which includes:
    - SimpleField: metadata-like fields (mostly used for filtering)
    - SearchableField: full-text search fields
    - VectorField: vector search fields
    The search index combines keyword and vector search into a hybrid format.

    If the index already exists, this function updates it.
    """
    search_index_client = get_search_index_client()

    # deleting the existing index
    if index_name in search_index_client.list_index_names():
        logger.debug(f"Index '{index_name}' already exists. Deleting it...")
        search_index_client.delete_index(index_name)

    logger.info(f"Creating vector index '{index_name}'...")

    # specify the configurations for vector search
    vector_search_config = VectorSearch(
        profiles=[
            VectorSearchProfile(
                name="default",
                algorithm_configuration_name="default-algo",
                vectorizer_name="azure_openai_text_3_large",
            )
        ],
        algorithms=[  # use HNSW approximate k-NN for vector search
            HnswAlgorithmConfiguration(
                name="default-algo",
                kind=VectorSearchAlgorithmKind.HNSW,
            )
        ],
        vectorizers=[  # use text-embedding-3-large for embedding query
            AzureOpenAIVectorizer(
                vectorizer_name="azure_openai_text_3_large",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=get_env_var("AZURE_OPENAI_PORTAL_ENDPOINT"),
                    api_key=get_env_var("AZURE_OPENAI_PORTAL_KEY"),
                    deployment_name="text-embedding-3-large",
                    model_name="text-embedding-3-large",
                ),
            )
        ],
    )

    # specify structure of the search index
    index = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SimpleField(  # not searchable, but filterable
                name="lecture_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
            SearchableField(  # searchable as may contain important keywords
                name="lecture_title",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SimpleField(  # not searchable, but filterable
                name="section_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
            ),
            SearchableField(  # searchable as may contain important keywords
                name="section_title",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchableField(  # searchable as may contain important keywords
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(  # searchable through vector search
                name="embedding",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single
                ),
                searchable=True,
                vector_search_dimensions=3072,
                vector_search_profile_name="default",
            ),
        ],
        vector_search=vector_search_config,
        # include a semantic reranker for improved search relevance
        semantic_search=SemanticSearch(
            default_configuration_name="semantic_config",
            configurations=[
                SemanticConfiguration(
                    name="semantic_config",
                    prioritized_fields=SemanticPrioritizedFields(
                        # prioritise content as search field as contain the
                        # heart of the written content. Though doesn't that
                        # exclude other searchable fields for semantic
                        # reranking?
                        content_fields=[SemanticField(field_name="content")]
                    ),
                )
            ],
        ),
    )

    search_index_client.create_index(index)  # create index in Azure AI Search
    logger.info(f"Vector index '{index_name}' created successfully.")


def add_chunks_to_index(
    index_name: str,
    chunks: list[EmbeddedSection],
) -> None:
    """
    Using the embedded sections and an Azure AI Search index
    name, this function pushes the chunks to the index.

    It mostly is a nice wrapper around SearchClient.upload_documents
    to ensure we handle errors and log progress.
    """
    search_client = SearchClient(
        endpoint=get_env_var("AZURE_SEARCH_ENDPOINT"),
        index_name=index_name,
        credential=AzureKeyCredential(get_env_var("AZURE_SEARCH_KEY")),
    )
    # convert Pydantic models to plain dicts
    docs = [doc.model_dump() for doc in chunks]

    logger.info(f"Uploading {len(docs)} chunks to index '{index_name}'...")
    result = search_client.upload_documents(documents=docs)
    failed = [r for r in result if not r.succeeded]
    if failed:  # keep track of failed uploads (never seen in practice)
        logger.error(f"{len(failed)} chunks failed to upload:")
        for f in failed:
            logger.error(f"- Chunk ID: {f.key}, Error: {f.error_message}")
    else:
        logger.info("All chunks uploaded successfully.")


def make_syllabus_search_index(
    syllabus: str,
    index_name: str,
    verbose: bool = False,
) -> None:
    """
    This functions wraps the process of creating a search index
    for the syllabus data:
    1. Chunks syllabus by section
    2. Generate and add embeddings to those chunks
    3. Set up the search index with relevant fields
    4. Push the chunks and embeddings to the search index
    """
    chunks = chunk_syllabus(syllabus, by="section")
    # we do not use get_aoai_client as this one is not
    # async and needed specifically for embedding
    client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=get_env_var("AZURE_OPENAI_ENDPOINT"),
        api_key=get_env_var("AZURE_OPENAI_KEY"),
    )
    embedded_chunks = create_embedding(
        client=client,
        syllabus_chunks=chunks,  # type: ignore
    )

    if verbose:  # for dev purposes, check the content of embedded chunks
        for chunk in embedded_chunks:
            print(f"L: {chunk.lecture_title}, S: {chunk.section_title}")
            print(f"E: {chunk.embedding[:5]} (len: {len(chunk.embedding)})")
            print("-" * 40)

    create_search_index(index_name)
    add_chunks_to_index(index_name, embedded_chunks)

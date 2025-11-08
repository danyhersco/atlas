import os
import re

from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient, PartitionKey

from utils.logger_config import logger


def upload_blob(
    blob_service_client: BlobServiceClient,
    local_filepath: str,
    container_name: str,
    base_filename: str,
) -> None:
    """
    Uploads a file to Azure Blob Storage with versioning and latest overwrite.

    This function uploads the file at `local_filepath` to the specified
    container in Azure Blob Storage. It first determines the next version
    number for the file and uploads a versioned copy. Then, it uploads
    (and overwrites) the file as the latest version using the base filename.

    Args:
        blob_service_client (BlobServiceClient): The Azure Blob Service client.
        local_filepath (str): Path to the local file to upload.
        container_name (str): Name of the blob container.
        base_filename (str): Base filename for the blob (without version).

    Returns:
        None
    """
    logger.debug(
        f"Uploading {os.path.basename(local_filepath)} "
        f"in container {container_name}..."
    )
    container_client = blob_service_client.get_container_client(container_name)

    base_name, ext = os.path.splitext(base_filename)
    version_pattern = re.compile(
        rf"{re.escape(base_name)}_v(\d+){re.escape(ext)}"
    )

    existing_blobs = container_client.list_blobs(name_starts_with=base_name)
    versions = [
        int(match.group(1))
        for blob in existing_blobs
        if (match := version_pattern.match(blob.name))
    ]
    next_version = max(versions, default=0) + 1
    versioned_name = f"{base_name}_v{next_version}{ext}"

    versioned_blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=versioned_name
    )
    with open(local_filepath, "rb") as f:
        versioned_blob_client.upload_blob(f)
    logger.info(f"Uploaded versioned blob: {versioned_name}")

    latest_blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=base_filename
    )
    with open(local_filepath, "rb") as f:
        latest_blob_client.upload_blob(f, overwrite=True)
    logger.info(f"Uploaded (and overwrote) latest blob: {base_filename}")


def get_blob(
    blob_service_client: BlobServiceClient,
    container_name: str,
    blob_name: str,
) -> str:
    """
    Retrieves the contents of a blob from Azure Blob Storage.

    This function downloads the specified blob from the given container
    and returns its contents decoded as a string. If retrieval fails,
    an error is logged and the exception is raised.

    Args:
        blob_service_client (BlobServiceClient): The Azure Blob Service client.
        container_name (str): Name of the blob container.
        blob_name (str): Name of the blob to retrieve.

    Returns:
        str: The contents of the blob as a UTF-8 string.

    Raises:
        Exception: If the blob cannot be retrieved or decoded.
    """

    logger.debug(
        f"Retrieving blob {blob_name} from container {container_name}..."
    )
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob=blob_name
    )
    try:
        blob_data = blob_client.download_blob().readall()
        return blob_data.decode("utf-8")
    except Exception as e:
        logger.error(f"Error retrieving blob {blob_name}: {e}")
        raise


def upsert_cosmos(
    cosmos_client: CosmosClient,
    documents: list[dict],
    container_name: str,
) -> None:
    """
    Upserts (inserts or updates) a list of documents
    into a Cosmos DB container.

    This function creates the database and container if they do not exist,
    then upserts each document in the provided list. Existing documents are
    updated, and new documents are inserted.

    Args:
        cosmos_client (CosmosClient): The Azure Cosmos DB client.
        documents (list[dict]): List of documents to upsert.
        container_name (str): Name of the Cosmos DB container.

    Returns:
        None
    """

    document_list_str = ", ".join(document["id"] for document in documents[:3])
    logger.debug(
        f"Upserting {len(documents)} documents with the first ids being "
        f"{document_list_str} in container {container_name}..."
    )
    database = cosmos_client.create_database_if_not_exists(id="campus")
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id"),
    )
    for document in documents:
        container.upsert_item(body=document)  # update if exist, insert if not
    logger.info(
        f"Upserted {len(documents)} documents with the first ids being "
        f"{document_list_str} in container {container_name}."
    )


def get_cosmos_docs_with_ids(
    cosmos_client: CosmosClient,
    container_name: str,
    document_ids: list[str],
) -> list[dict]:
    """
    Retrieves documents from a Cosmos DB container by their IDs.

    Args:
        cosmos_client (CosmosClient): The Azure Cosmos DB client.
        container_name (str): Name of the Cosmos DB container.
        document_ids (list[str]): List of document IDs to retrieve.

    Returns:
        list[dict]: List of retrieved documents as dictionaries.

    Raises:
        Exception: If any document retrieval fails.
    """

    logger.debug(
        f"Retrieving {len(document_ids)} document from container "
        f"{container_name}, with ids {', '.join(document_ids[:3])}, etc..."
    )
    database = cosmos_client.get_database_client("campus")
    container = database.get_container_client(container_name)

    try:
        documents = []
        for document_id in document_ids:
            document = container.read_item(
                item=document_id, partition_key=document_id
            )
            document = {  # ignore fields internal to Azure that start with _
                k: v for k, v in document.items() if not k.startswith("_")
            }
            documents.append(document)
        return documents
    except Exception as e:
        logger.error(f"Error retrieving documents: {e}")
        raise


def get_cosmos_docs_with_fields(
    cosmos_client: CosmosClient,
    container_name: str,
    fields: dict[str, str],
) -> list[dict]:
    """
    Retrieves documents from a Cosmos DB container that
    match specified field values.

    Args:
        cosmos_client (CosmosClient): The Azure Cosmos DB client.
        container_name (str): Name of the Cosmos DB container.
        fields (dict[str, str]): Dictionary of field names and values to match.

    Returns:
        list[dict]: List of retrieved documents as dictionaries.
            Returns an empty list if no matches are found.

    Raises:
        Exception: If the query fails.
    """
    database = cosmos_client.get_database_client("campus")
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id"),
    )

    logger.info(
        f"Looking for documents in {container_name} with fields {fields}"
    )

    where_clauses = []
    params = []

    # create a parameterized query
    for i, (field, value) in enumerate(fields.items()):
        param_name = f"@field_value_{i}"
        where_clauses.append(f"c.{field} = {param_name}")
        params.append({"name": param_name, "value": value})

    # build the query
    where_statement = " AND ".join(where_clauses)
    query = f"SELECT * FROM c WHERE {where_statement}"

    # get query results
    results = list(
        container.query_items(
            query=query,
            parameters=params,  # type: ignore
            enable_cross_partition_query=True,
        )
    )

    if not results:
        error = f"No documents found in {container_name} with fields {fields}"
        logger.warning(error)
        return []

    results = [  # ignore fields internal to Azure that start with _
        {k: v for k, v in doc.items() if not k.startswith("_")}
        for doc in results
    ]

    logger.info(f"Found and retrieved {len(results)} documents.")

    return results


def delete_cosmos_with_fields(
    cosmos_client: CosmosClient,
    container_name: str,
    fields: dict[str, str],
) -> None:
    """
    Deletes documents from a Cosmos DB container that match
    specified field values.

    Args:
        cosmos_client (CosmosClient): The Azure Cosmos DB client.
        container_name (str): Name of the Cosmos DB container.
        fields (dict[str, str]): Dictionary of field names and values to match.

    Returns:
        None
    """
    database = cosmos_client.get_database_client("campus")
    container = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id"),
    )

    results = get_cosmos_docs_with_fields(
        cosmos_client=cosmos_client,
        container_name=container_name,
        fields=fields,
    )

    result_ids_str = ", ".join(doc["id"] for doc in results[:3])
    logger.warning(
        f"Deleting {len(results)} document (i.e. {result_ids_str}, etc)."
    )

    for doc in results:
        doc_id = doc["id"]
        container.delete_item(item=doc_id, partition_key=doc_id)

    logger.info(f"Deleted {len(results)} documents.")

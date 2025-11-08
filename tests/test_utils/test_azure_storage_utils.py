from unittest.mock import MagicMock, mock_open, patch
from utils.azure_storage_utils import (
    upload_blob,
    upsert_cosmos,
    get_blob,
    get_cosmos_docs_with_ids,
    get_cosmos_docs_with_fields,
    delete_cosmos_with_fields,
)


@patch("builtins.open", new_callable=mock_open, read_data=b"file content")
def test_upload_blob(mock_file):
    blob_service_client = MagicMock()
    container_client = MagicMock()
    blob_service_client.get_container_client.return_value = container_client

    mock_blob1 = MagicMock()
    mock_blob1.name = "file_v1.pdf"

    mock_blob2 = MagicMock()
    mock_blob2.name = "file_v2.pdf"

    container_client.list_blobs.return_value = [mock_blob1, mock_blob2]

    blob_service_client.get_blob_client.return_value = MagicMock()

    upload_blob(
        blob_service_client=blob_service_client,
        local_filepath="dummy/file.pdf",
        container_name="test-container",
        base_filename="file.pdf",
    )

    assert blob_service_client.get_blob_client.call_count == 2
    assert mock_file.call_count == 2
    container_client.list_blobs.assert_called_once_with(
        name_starts_with="file"
    )


def test_upsert_cosmos():
    cosmos_client = MagicMock()
    database = MagicMock()
    container = MagicMock()

    cosmos_client.create_database_if_not_exists.return_value = database
    database.create_container_if_not_exists.return_value = container

    document = {"id": "doc1", "name": "test"}

    upsert_cosmos(
        cosmos_client=cosmos_client,
        documents=[document],
        container_name="test-container",
    )

    cosmos_client.create_database_if_not_exists.assert_called_once_with(
        id="campus"
    )
    database.create_container_if_not_exists.assert_called_once()
    container.upsert_item.assert_called_once_with(body=document)


def test_get_blob():
    """Test the get_blob function."""
    blob_service_client = MagicMock()
    blob_client = MagicMock()
    mock_blob_data = MagicMock()

    # Mock the blob client and its download_blob method
    blob_service_client.get_blob_client.return_value = blob_client
    blob_client.download_blob.return_value = mock_blob_data
    mock_blob_data.readall.return_value = b"test content"

    result = get_blob(
        blob_service_client=blob_service_client,
        container_name="test-container",
        blob_name="test-blob.txt",
    )

    # Verify the result
    assert result == "test content"

    # Verify the blob client was called correctly
    blob_service_client.get_blob_client.assert_called_once_with(
        container="test-container", blob="test-blob.txt"
    )
    blob_client.download_blob.assert_called_once()
    mock_blob_data.readall.assert_called_once()


def test_get_cosmos_docs_with_ids():
    """Test the get_cosmos_docs_with_ids function."""
    cosmos_client = MagicMock()
    database = MagicMock()
    container = MagicMock()

    # Mock the database and container clients
    cosmos_client.get_database_client.return_value = database
    database.get_container_client.return_value = container

    # Mock document data
    mock_doc1 = {"id": "doc1", "name": "test1", "_etag": "etag1"}
    mock_doc2 = {"id": "doc2", "name": "test2", "_etag": "etag2"}

    container.read_item.side_effect = [mock_doc1, mock_doc2]

    result = get_cosmos_docs_with_ids(
        cosmos_client=cosmos_client,
        container_name="test-container",
        document_ids=["doc1", "doc2"],
    )

    # Verify the result (internal Azure fields should be filtered out)
    assert len(result) == 2
    assert result[0] == {"id": "doc1", "name": "test1"}
    assert result[1] == {"id": "doc2", "name": "test2"}

    # Verify the database and container clients were called correctly
    cosmos_client.get_database_client.assert_called_once_with("campus")
    database.get_container_client.assert_called_once_with("test-container")

    # Verify read_item was called for each document ID
    assert container.read_item.call_count == 2
    container.read_item.assert_any_call(item="doc1", partition_key="doc1")
    container.read_item.assert_any_call(item="doc2", partition_key="doc2")


def test_get_cosmos_docs_with_fields():
    """Test the get_cosmos_docs_with_fields function."""
    cosmos_client = MagicMock()
    database = MagicMock()
    container = MagicMock()

    # Mock the database and container clients
    cosmos_client.get_database_client.return_value = database
    database.create_container_if_not_exists.return_value = container

    # Mock query results
    mock_results = [
        {"id": "doc1", "name": "test1", "_etag": "etag1"},
        {"id": "doc2", "name": "test2", "_etag": "etag2"},
    ]
    container.query_items.return_value = mock_results

    result = get_cosmos_docs_with_fields(
        cosmos_client=cosmos_client,
        container_name="test-container",
        fields={"name": "test", "status": "active"},
    )

    # Verify the result (internal Azure fields should be filtered out)
    assert len(result) == 2
    assert result[0] == {"id": "doc1", "name": "test1"}
    assert result[1] == {"id": "doc2", "name": "test2"}

    # Verify the database and container clients were called correctly
    cosmos_client.get_database_client.assert_called_once_with("campus")
    database.create_container_if_not_exists.assert_called_once()

    # Verify query_items was called with the correct query
    container.query_items.assert_called_once()
    call_args = container.query_items.call_args
    assert (
        "SELECT * FROM c WHERE c.name = @field_value_0 "
        "AND c.status = @field_value_1"
    ) in call_args[1]["query"]
    assert call_args[1]["enable_cross_partition_query"] is True


def test_delete_cosmos_with_fields():
    """Test the delete_cosmos_with_fields function."""
    cosmos_client = MagicMock()
    database = MagicMock()
    container = MagicMock()

    # Mock the database and container clients
    cosmos_client.get_database_client.return_value = database
    database.create_container_if_not_exists.return_value = container

    # Mock the get_cosmos_docs_with_fields function to return test documents
    with patch(
        "utils.azure_storage_utils.get_cosmos_docs_with_fields"
    ) as mock_get_docs:
        mock_get_docs.return_value = [
            {"id": "doc1", "name": "test1"},
            {"id": "doc2", "name": "test2"},
        ]

        delete_cosmos_with_fields(
            cosmos_client=cosmos_client,
            container_name="test-container",
            fields={"name": "test"},
        )

        # Verify get_cosmos_docs_with_fields was called
        mock_get_docs.assert_called_once_with(
            cosmos_client=cosmos_client,
            container_name="test-container",
            fields={"name": "test"},
        )

        # Verify delete_item was called for each document
        assert container.delete_item.call_count == 2
        container.delete_item.assert_any_call(
            item="doc1", partition_key="doc1"
        )
        container.delete_item.assert_any_call(
            item="doc2", partition_key="doc2"
        )

from functools import lru_cache

from azure.storage.blob import BlobServiceClient
from azure.cosmos import CosmosClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from openai import AsyncAzureOpenAI

from utils.get_env_var import get_env_var


@lru_cache(maxsize=1)
def get_blob_service_client() -> BlobServiceClient:
    """
    Lazily retrieves an Azure Blob Storage Client
    """
    return BlobServiceClient(
        account_url=get_env_var("BLOB_STORAGE_URL"),
        credential=get_env_var("BLOB_STORAGE_KEY"),
    )


@lru_cache(maxsize=1)
def get_cosmos_client() -> CosmosClient:
    """
    Lazily retrieves an Azure Cosmos DB Client
    """
    return CosmosClient(
        url=get_env_var("COSMOS_URI"),
        credential=get_env_var("COSMOS_KEY"),
    )


@lru_cache(maxsize=1)
def get_aoai_client() -> AsyncAzureOpenAI:
    """
    Lazily retrieves an (Async) Azure OpenAI Client
    """
    return AsyncAzureOpenAI(
        api_version="2024-12-01-preview",
        api_key=get_env_var("AZURE_OPENAI_KEY"),
        azure_endpoint=get_env_var("AZURE_OPENAI_ENDPOINT"),
    )


@lru_cache
def get_search_index_client() -> SearchIndexClient:
    """
    Lazily retrieves an Azure Search Index Client
    """
    return SearchIndexClient(
        endpoint=get_env_var("AZURE_SEARCH_ENDPOINT"),
        credential=AzureKeyCredential(get_env_var("AZURE_SEARCH_KEY")),
    )

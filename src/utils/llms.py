from enum import StrEnum

from pydantic import BaseModel
from utils.get_env_var import get_env_var


class LLMName(StrEnum):
    """Deployment names for various LLMs."""

    GPT_5_CHAT = "gpt-5-chat"
    GPT_5_MINI = "gpt-5-mini"
    O3_MINI = "o3-mini"
    GPT_41_NANO = "gpt-4.1-nano"
    GPT_41_MINI = "gpt-4.1-mini"
    GPT_41 = "gpt-4.1"
    GPT_4O = "gpt-4o"
    GPT_35_TURBO = "gpt-35-turbo"


class LLM(BaseModel):
    name: str
    key: str
    endpoint: str


def get_llm(name: LLMName) -> LLM:
    """
    Retrieves Azure OpenAI deployment credentials for a specified LLM.

    This function loads the API key and endpoint for the given LLM name
    from environment variables, and returns an LLM object containing the
    deployment name, key, and endpoint URL.

    Args:
        name (LLMName): The name of the LLM deployment to retrieve.

    Returns:
        LLM: An object containing the deployment name, API key,
            and endpoint URL.

    Raises:
        ValueError: If the LLM name is unknown or not configured.
    """

    key = get_env_var("AZURE_OPENAI_KEY")
    endpoint_env_keys = {
        LLMName.GPT_5_CHAT: "GPT_5_CHAT",
        LLMName.GPT_5_MINI: "GPT_5_MINI",
        LLMName.O3_MINI: "GPT_O3_MINI_ENDPOINT",
        LLMName.GPT_41_NANO: "GPT_41_NANO_ENDPOINT",
        LLMName.GPT_41_MINI: "GPT_41_MINI_ENDPOINT",
        LLMName.GPT_41: "GPT_41_ENDPOINT",
        LLMName.GPT_4O: "GPT_4O_ENDPOINT",
        LLMName.GPT_35_TURBO: "GPT_35_TURBO_ENDPOINT",
    }

    if name not in endpoint_env_keys:
        raise ValueError(f"Unknown LLM name: {name}")

    return LLM(
        name=name.value,
        key=key,
        endpoint=get_env_var(endpoint_env_keys[name]),
    )

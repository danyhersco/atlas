from openai import AsyncAzureOpenAI
from typing import TypeVar, Union
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)


async def generate(
    client: AsyncAzureOpenAI,
    system_prompt: str,
    user_prompt: str,
    llm: str,
    output_format: type[T] | None = None,
) -> Union[str, T]:
    """
    Generates a chat completion using Azure OpenAI,
    optionally parsing the output to a Pydantic model.

    This function sends a system prompt and user prompt to the
    specified LLM deployment. If an output_format (Pydantic model)
    is provided, the response is parsed into that model. Otherwise,
    the raw string response is returned.

    Args:
        client (AsyncAzureOpenAI): The (async) Azure OpenAI client.
        system_prompt (str): The system prompt for the assistant.
        user_prompt (str): The user's prompt or question.
        llm (str): The LLM deployment name.
        output_format (type[T] | None, optional): Pydantic model type
            to parse the response.

    Returns:
        Union[str, T]: The generated response as a string or parsed
            Pydantic model.

    Raises:
        ValueError: If no output is returned from the LLM.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    if output_format is not None:
        response = await client.beta.chat.completions.parse(
            messages=messages,  # type: ignore
            model=llm,
            response_format=output_format,  # type: ignore
        )
        output = response.choices[0].message.parsed
    else:
        response = await client.chat.completions.create(
            messages=messages,  # type: ignore
            model=llm,
        )
        output = response.choices[0].message.content

    if output is None:
        raise ValueError("Error generating Chat Completion: None returned.")

    return output

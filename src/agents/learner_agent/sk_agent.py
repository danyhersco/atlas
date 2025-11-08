from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (  # noqa: E501
    AzureChatPromptExecutionSettings,
)

from models.base import Course
from utils.llms import get_llm, LLMName
from utils.logger_config import logger
from agents.learner_agent.base import LearnerAgent


class SKLearnerAgent(LearnerAgent):
    def __init__(self, course: Course, learner_id: str, model_name: str):
        super().__init__(course, learner_id, model_name)
        self.llm = get_llm(name=LLMName(model_name))

        self.kernel = Kernel()  # init kernel
        self.agent = AzureChatCompletion(
            deployment_name=self.llm.name,
            api_key=self.llm.key,
            endpoint=self.llm.endpoint,
        )
        self.kernel.add_service(self.agent)  # add chat service
        self.chat_history = ChatHistory()  # init chat history

    async def process_message(self, message: str, trunc: int = 7) -> str:
        """
        Extension from abstractmethod:

        The system message is updated every turn, to reflect the current
        KC being taught and the prior knowledge status the learner needs
        to behave according to.
        """
        logger.debug(f"Sending message to student: {message[:20]}")
        self.chat_history.add_user_message(message)

        system_message = ChatMessageContent(  # re-form system prompt
            role=AuthorRole.SYSTEM, content=self.make_instructions()
        )

        # truncate messages if exceeds the messages length
        messages_to_keep = self.chat_history.messages[-trunc:]
        # we of course do not truncate system prompt
        self.chat_history.messages = [system_message] + messages_to_keep

        response = await self.agent.get_chat_message_content(
            chat_history=self.chat_history,
            settings=AzureChatPromptExecutionSettings(),
        )
        if response is None:
            error_message = "No content returned from student agent."
            logger.error(error_message)
            raise ValueError(error_message)

        self.chat_history.add_assistant_message(response.content)
        self.chat_history.messages.pop(0)  # remove system prompt
        return response.content

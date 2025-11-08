from azure.ai.language.conversations import ConversationAnalysisClient
from azure.identity import DefaultAzureCredential
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

from utils.logger_config import logger
from utils.get_env_var import get_env_var


class SummaryManager:
    def __init__(self):
        self.client = ConversationAnalysisClient(
            endpoint=get_env_var("AZURE_AI_SERVICES_ENDPOINT"),
            credential=DefaultAzureCredential(),
        )

    def summarise(self, chat_history: ChatHistory) -> None:
        logger.debug("Summarising chat history...")

        conversation_items = self.messages_to_conversation_items(
            chat_history.messages
        )

        task = {
            "displayName": "Summarise the conversation rounds",
            "analysisInput": {
                "conversations": [
                    {
                        "conversationItems": conversation_items,
                        "modality": "text",
                        "id": "conversation1",
                        "language": "en",
                    },
                ]
            },
            "tasks": [
                {
                    "taskName": "Narrative task",
                    "kind": "ConversationalSummarizationTask",
                    "parameters": {"summaryAspects": ["narrative"]},
                },
            ],
        }

        with self.client:
            poller = self.client.begin_conversation_analysis(task=task)

            result = poller.result()
            task_results = result["tasks"]["items"]
            for task in task_results:
                print(f"\n{task['taskName']} status: {task['status']}")
                task_result = task["results"]
                if task_result["errors"]:
                    print("... errors occurred ...")
                    for error in task_result["errors"]:
                        print(error)
                else:
                    conversation_result = task_result["conversations"][0]
                    if conversation_result["warnings"]:
                        print("... view warnings ...")
                        for warning in conversation_result["warnings"]:
                            print(warning)
                    else:
                        summaries = conversation_result["summaries"]
                        for summary in summaries:
                            print(f"{summary['aspect']}: {summary['text']}")

    def messages_to_conversation_items(
        self, messages: list[ChatMessageContent]
    ) -> list[dict]:
        conversation_items = []
        for i, message in enumerate(messages):
            if message.role in (AuthorRole.USER, AuthorRole.ASSISTANT):
                conversation_item = {
                    "text": message.content,
                    "id": i + 1,
                    "role": message.role.value,
                    "participantId": message.role.value,
                }
                conversation_items.append(conversation_item)

        return conversation_items

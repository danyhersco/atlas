import ollama

from models.base import Course
from agents.learner_agent.base import LearnerAgent
from utils.logger_config import logger


class OllamaLearnerAgent(LearnerAgent):
    def __init__(self, course: Course, learner_id: str, model_name: str):
        super().__init__(course, learner_id, model_name)
        self.chat_history = [
            {"role": "system", "content": self.make_instructions()}
        ]

    async def process_message(self, message: str, trunc: int = 7) -> str:
        logger.debug(f"Sending message to student: {message[:20]}")
        self.chat_history.append({"role": "user", "content": message})

        # truncate chat history if it exceeds the maximum length
        if len(self.chat_history) > trunc:
            truncated_history = (
                self.chat_history[:1] + self.chat_history[-trunc:]
            )
        else:
            truncated_history = self.chat_history

        # get ollama response
        response = ollama.chat(
            model=self.model_name, messages=truncated_history
        )
        response = response["message"]["content"]

        self.chat_history.append({"role": "assistant", "content": response})
        return response

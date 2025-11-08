import chainlit as cl

from agents.atlas_agent import AtlasAgent
from education_data.course.data import COURSES
from education_data.learner.data import LEARNERS
from models.base import CourseID
from utils.logger_config import logger


learner_id = "learner_10"
learner = LEARNERS[learner_id]


@cl.password_auth_callback  # type: ignore
def auth_callback(username: str, password: str) -> cl.User | None:
    """TODO: Supposed to work but not working yet."""
    logger.debug(f"Authenticating user: {username}")
    user_password_pairs = [("dev", "atlas")]
    if (username, password) in user_password_pairs:
        logger.info(f"User {username} authenticated successfully.")
        return cl.User(identifier=username)
    else:
        logger.error(f"Authentication failed for user: {username}")
        return None


@cl.set_starters  # type: ignore
async def set_starters():
    logger.warning("RUNNING SET STARTERS...")
    return [
        cl.Starter(
            label="Let's pursue my progress!",
            message="Let's pursue my progress!",
        ),
        cl.Starter(
            label="Where did we last stop?",
            message="Where did we last stop?",
        ),
        cl.Starter(
            label="What are my knowledge gaps?",
            message="What are my knowledge gaps?",
        ),
    ]


@cl.set_chat_profiles  # type: ignore
async def chat_profile():
    logger.warning("RUNNING SET CHAT PROFILES...")
    logger.debug("Setting chat profiles...")
    chat_profiles = [
        cl.ChatProfile(
            name=course_id.value,
            markdown_description=f"Your {course_id.value} personal tutor",
            icon=f"public/avatars/{course_id.value.lower()}.png",
        )
        for course_id in learner.course_ids
    ]
    logger.info(
        f"{len(chat_profiles)} chat profiles created for {learner.name}."
    )
    return chat_profiles


@cl.on_chat_start
async def on_chat_start():
    logger.warning("RUNNING ON CHAT START...")
    chat_profile = cl.user_session.get("chat_profile")
    course = COURSES[CourseID(chat_profile)]
    model_name = "gpt-5-chat"

    mcp_plugin = await AtlasAgent.mcp_connect()
    agent_manager = AtlasAgent(course, learner_id, mcp_plugin, model_name)
    _ = cl.SemanticKernelFilter(kernel=agent_manager.kernel)

    cl.user_session.set("agent_manager", agent_manager)
    cl.user_session.set("mcp_plugin", mcp_plugin)


@cl.on_message
async def main(message: cl.Message):
    logger.warning("RUNNING ON MESSAGE...")
    agent_manager = cl.user_session.get("agent_manager")

    if not isinstance(agent_manager, AtlasAgent):
        raise ValueError(
            "Retrieved 'agent_manager' is not of type AgentManager."
        )

    msg = cl.Message(content="")

    async for chunk in agent_manager.process_learner_message(message.content):
        await msg.stream_token(chunk)

    await msg.update()


@cl.on_chat_end
async def on_chat_end():
    logger.warning("RUNNING ON CHAT END...")
    mcp_plugin = cl.user_session.get("mcp_plugin")
    await AtlasAgent.mcp_disconnect(mcp_plugin)  # type: ignore

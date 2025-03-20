from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel

default_llm: BaseChatModel = ChatAnthropic(model="claude-3-5-sonnet-20240620")

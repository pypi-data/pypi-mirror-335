from typing import Callable, Dict, List, Type, TypeVar, cast
from datetime import datetime

from langchain_core.messages import ToolMessage, BaseMessage
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import ValidationError, BaseModel, Field
from langchain_core.language_models import BaseChatModel


class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing.")
    superfluous: str = Field(description="Critique of what is superfluous")


class AnswerQuestion(BaseModel):
    """Answer the question. Provide an answer, reflection, and then follow up with search queries to improve the answer."""

    answer: str = Field(description="~250 word detailed answer to the question.")
    reflection: Reflection = Field(description="Your reflection on the initial answer.")
    search_queries: List[str] = Field(
        description="1-3 search queries for researching improvements to address the critique of your current answer."
    )


T = TypeVar("T")


class ResponderWithRetries:
    def __init__(self, runnable: Runnable, validator: PydanticToolsParser):
        self.runnable = runnable
        self.validator = validator

    def respond(
        self, state: Dict[str, List[BaseMessage]]
    ) -> Dict[str, List[BaseMessage]]:
        response: List[BaseMessage] = []
        for attempt in range(3):
            response = cast(
                List[BaseMessage],
                self.runnable.invoke(
                    {"messages": state["messages"]},
                    cast(RunnableConfig, {"tags": [f"attempt:{attempt}"]}),
                ),
            )
            try:
                self.validator.invoke(response)
                return {"messages": response}
            except ValidationError as e:
                state = {
                    "messages": state["messages"]
                    + [
                        response[-1],  # type: ignore
                        ToolMessage(
                            content=f"{repr(e)}\n\nPay close attention to the function schema.\n\n"
                            + self.validator.model_json_schema()
                            + " Respond by fixing all validation errors.",
                            tool_call_id=response[-1].tool_calls[0]["id"],  # type: ignore
                        ),
                    ]
                }
        return {"messages": response}


class PromptTemplateBuilder:
    """
    A builder class for creating and configuring prompt templates consistently.
    This centralizes template creation and provides a way to customize
    different aspects of the template for various use cases.
    """

    def __init__(
        self, system_template: str = None, time_provider: Callable[[], str] = None
    ):
        """
        Initialize the template builder with optional customizations.

        Args:
            system_template: The system message template to use. If None, a default is provided.
            time_provider: A function that returns the current time as a string.
                           If None, the default uses ISO format datetime.
        """
        self.system_template = (
            system_template
            or """You are expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. Recommend search queries to research information and improve your answer."""
        )

        self.time_provider = time_provider or (lambda: datetime.now().isoformat())

    def create_base_template(self) -> ChatPromptTemplate:
        """
        Create a base prompt template with the system message and message placeholder.

        Returns:
            A ChatPromptTemplate with the system message and a placeholder for user messages.
        """
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    self.system_template,
                ),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "user",
                    "\n\n<system>Reflect on the user's original question and the"
                    " actions taken thus far. Respond using the {function_name} function.</reminder>",
                ),
            ]
        ).partial(
            time=self.time_provider,
        )

    def create_template_with_instruction(
        self, first_instruction: str, function_name: str
    ) -> ChatPromptTemplate:
        """
        Create a prompt template with specific instruction and function name.

        Args:
            first_instruction: The primary instruction to include in the template.
            function_name: The name of the function to use for the response.

        Returns:
            A ChatPromptTemplate configured with the provided instruction and function name.
        """
        base_template = self.create_base_template()
        return base_template.partial(
            first_instruction=first_instruction,
            function_name=function_name,
        )

    def create_chain(
        self, first_instruction: str, tool_class: Type[BaseModel], llm: BaseChatModel
    ) -> Runnable:
        """
        Create a complete chain with the template, instruction, function class, and LLM.

        Args:
            first_instruction: The primary instruction for the template.
            tool_class: The pydantic model class to use as a tool.
            llm: The LLM to bind the tools to.

        Returns:
            A runnable chain that combines the template and the LLM with bound tools.
        """
        template = self.create_template_with_instruction(
            first_instruction=first_instruction,
            function_name=tool_class.__name__,
        )

        return template | llm.bind_tools(tools=[tool_class])

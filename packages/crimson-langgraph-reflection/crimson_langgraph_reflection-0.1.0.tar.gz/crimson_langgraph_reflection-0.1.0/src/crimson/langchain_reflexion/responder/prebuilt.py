from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.runnables import Runnable
from typing import List
from pydantic import Field

from .base import ResponderWithRetries, AnswerQuestion, PromptTemplateBuilder
from ..llm import default_llm

qna_validator: PydanticToolsParser = PydanticToolsParser(tools=[AnswerQuestion])

prompt_builder = PromptTemplateBuilder()


class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question. Provide an answer, reflection,

    cite your reflection with references, and finally
    add search queries to improve the answer."""

    references: List[str] = Field(
        description="Citations motivating your updated answer."
    )


revise_instructions: str = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
        - You MUST include numerical citations in your revised answer to ensure it can be verified.
        - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
            - [1] https://example.com
            - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
"""


class ResponderHolder:
    """
    A container class that holds responder components used in the LangChain Reflexion system.

    This class provides organized access to the different responder components with
    documentation about their purpose and functionality. Each responder is responsible
    for a specific part of the reflexive answering process.
    """

    def __init__(self, llm=None):
        self.llm = llm if llm else default_llm

    @property
    def first_responder(self) -> ResponderWithRetries:
        """
        The initial responder component that generates the first answer to a user's question.

        This responder creates a detailed answer, reflects on what might be missing or superfluous,
        and generates search queries to gather more information for improvement.

        Returns:
            ResponderWithRetries: The first responder component.
        """

        initial_answer_chain: Runnable = prompt_builder.create_chain(
            first_instruction="Provide a detailed ~250 word answer.",
            tool_class=AnswerQuestion,
            llm=default_llm,
        )

        _first_responder: ResponderWithRetries = ResponderWithRetries(
            runnable=initial_answer_chain, validator=qna_validator
        )

        return _first_responder

    @property
    def revisor(self) -> ResponderWithRetries:
        """
        The revision responder component that improves answers with new information.

        This responder takes the initial answer and search results, then produces an
        improved answer with citations to verify the information. It continues the
        reflection process and may generate additional search queries for further improvement.

        Returns:
            ResponderWithRetries: The revision responder component.
        """

        revision_chain: Runnable = prompt_builder.create_chain(
            first_instruction=revise_instructions,
            tool_class=ReviseAnswer,
            llm=default_llm,
        )

        revision_qna_validator: PydanticToolsParser = PydanticToolsParser(
            tools=[ReviseAnswer]
        )

        _revisor: ResponderWithRetries = ResponderWithRetries(
            runnable=revision_chain, validator=revision_qna_validator
        )

        return _revisor


responder_holder = ResponderHolder()

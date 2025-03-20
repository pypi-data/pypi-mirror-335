from dotenv import load_dotenv

load_dotenv()

from typing import Annotated, List, Literal
from typing_extensions import TypedDict
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph, START
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages

from .responder import ResponderHolder
from .tool import tool_node


# Define the state type for the graph
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


# Define looping logic:
def _get_num_iterations(state: list) -> int:
    i = 0
    for m in state["messages"][::-1]:
        if m.type not in {"tool", "ai"}:
            break
        i += 1
    return i


def create_base_graph(
    llm: BaseChatModel = None, max_iterations: int = 5
) -> CompiledStateGraph:
    """
    Creates a base reflection graph that implements the standard question-answering workflow.

    This function generates a graph that follows the original example implementation
    with the draft -> execute_tools -> revise workflow. It allows for basic customization
    through the LLM model and iteration count parameters without requiring additional
    modifications to the core structure.

    Args:
        llm: Optional custom language model to use. If None, the default LLM will be used.
        max_iterations: Maximum number of reflection cycles to perform (default: 5).

    Returns:
        A compiled state graph ready to be executed.
    """

    responder_holder = ResponderHolder(llm=llm)

    def event_loop(state: list) -> Literal["execute_tools", END]:
        # in our case, we'll just stop after N plans
        num_iterations = _get_num_iterations(state)
        if num_iterations > max_iterations:
            return END
        return "execute_tools"

    builder: StateGraph = StateGraph(State)

    # Add nodes to the graph
    builder.add_node("draft", responder_holder.first_responder.respond)
    builder.add_node("execute_tools", tool_node)
    builder.add_node("revise", responder_holder.revisor.respond)

    # Connect the nodes
    # draft -> execute_tools
    builder.add_edge("draft", "execute_tools")
    # execute_tools -> revise
    builder.add_edge("execute_tools", "revise")
    # Add conditional edge
    builder.add_conditional_edges("revise", event_loop, ["execute_tools", END])

    # Set the starting node
    builder.add_edge(START, "draft")

    graph = builder.compile()

    return graph


def create_graph(
    llm: BaseChatModel = None, max_iterations: int = 5
) -> CompiledStateGraph:
    """
    A placeholder function for future customized graph creation implementations.

    Currently, this function simply forwards to create_base_graph, but exists as an
    extension point for gradually generalizing and expanding the module beyond the
    basic example. As the module evolves, this function can be enhanced to support
    more advanced configurations without changing the public API.

    Args:
        llm: Optional custom language model to use. If None, the default LLM will be used.
        max_iterations: Maximum number of reflection cycles to perform (default: 5).

    Returns:
        A compiled state graph ready to be executed.
    """
    return create_base_graph(llm, max_iterations)

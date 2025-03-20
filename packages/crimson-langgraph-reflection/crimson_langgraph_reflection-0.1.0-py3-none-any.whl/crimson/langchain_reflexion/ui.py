from langchain_core.runnables import RunnableConfig
from .graph import create_base_graph
from langchain_core.language_models.chat_models import BaseChatModel
from typing import Optional


def stream_shortcut(
    question: str,
    llm: Optional[BaseChatModel] = None,
    max_iterations: int = 5,
    config: RunnableConfig = None,
    skip: bool = False,
):
    """
    A convenience function to quickly test the reflection system with a question.

    This function creates and runs the reflection graph with the provided question,
    displaying each step of the process in the console. It serves as a shortcut
    for trying out the system without needing to set up the full graph manually.

    Args:
        question: The question to process through the reflection system
        llm: Optional custom language model to use (default: None uses the default LLM)
        max_iterations: Maximum number of reflection cycles to perform (default: 5)
        config: Optional runnable configuration for the graph

    Returns:
        None - Results are printed to the console
    """

    if skip:
        print("Skipping the graph execution.")
        return

    graph = create_base_graph(llm=llm, max_iterations=max_iterations)

    events = graph.stream(
        {"messages": [("user", question)]},
        stream_mode="values",
        config=config,
    )
    for i, step in enumerate(events):
        print(f"Step {i}")
        step["messages"][-1].pretty_print()

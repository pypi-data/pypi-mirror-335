from typing import Dict, List, Any

from langchain_core.tools import StructuredTool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langgraph.prebuilt import ToolNode

from .responder import AnswerQuestion
from .responder.prebuilt import ReviseAnswer

search: TavilySearchAPIWrapper = TavilySearchAPIWrapper()
tavily_tool: TavilySearchResults = TavilySearchResults(
    api_wrapper=search, max_results=5
)


def run_queries(search_queries: List[str]) -> List[Dict[str, Any]]:
    """Run the generated queries."""
    return tavily_tool.batch([{"query": query} for query in search_queries])


tool_node: ToolNode = ToolNode(
    [
        StructuredTool.from_function(run_queries, name=AnswerQuestion.__name__),
        StructuredTool.from_function(run_queries, name=ReviseAnswer.__name__),
    ]
)

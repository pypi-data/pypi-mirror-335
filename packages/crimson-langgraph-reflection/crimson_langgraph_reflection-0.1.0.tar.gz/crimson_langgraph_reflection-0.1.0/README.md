# Crimson Langgraph Reflection

A modular implementation of LangChain's [Reflexion](https://langchain-ai.github.io/langgraph/tutorials/reflexion/reflexion/) example, designed to make agent development more accessible, extensible, and reusable.

## Overview

This project transforms the original LangChain Reflexion tutorial into a fully modular package. The Reflexion pattern enables LLM agents to:

1. Answer questions
2. Reflect on and critique their own answers 
3. Generate search queries to gather more information
4. Revise answers based on new information

By modularizing this pattern, this package aims to:
- Make Reflexion-style agents easier to implement in your projects
- Provide a solid foundation for further customization and extension
- Encourage reusability of core Reflexion components

## Installation

```bash
pip install crimson-langgraph-reflection
```

## Key Components

The package is organized into several main modules:

- **graph.py**: Defines the LangGraph state machine that orchestrates the reflection process
- **responder/**: Contains components for generating answers, reflections, and search queries
  - **base.py**: Core classes for response generation and validation
  - **prebuilt.py**: Ready-to-use responder implementations
- **tool.py**: Search tool integration for information gathering
- **ui.py**: Simple interface for running the Reflexion agent
- **llm.py**: LLM configuration (defaulting to Claude 3.5 Sonnet)

## Quick Start

```python
from crimson.langchain_reflexion.ui import stream_shortcut

# Run with default settings (5 iterations)
stream_shortcut(question="What is LangChain?")

# Or customize the number of iterations
stream_shortcut(
    question="What is LangChain?",
    max_iterations=3
)

# Use a custom LLM
from langchain_anthropic import ChatAnthropic
custom_llm = ChatAnthropic(model="claude-3-opus-20240229")

stream_shortcut(
    question="What is LangChain?",
    llm=custom_llm
)
```

## Examples

For complete examples, check out:
- [Example Notebook](https://github.com/crimson206/langgraph-reflection/blob/main/example/reflexion_ui.ipynb)

## Extension and Customization

This package is designed to be extensible. You can:

1. Create custom responder implementations by extending the base classes
2. Modify the graph structure to add additional steps
3. Integrate different search or reasoning tools
4. Adjust the system prompts and reflection criteria

## Requirements

- Python ≥ 3.9
- LangChain
- LangGraph
- Anthropic API access (for default LLM)

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgements

This project is based on LangChain's Reflexion tutorial. Special thanks to the LangChain team for their innovative work on LLM agent frameworks.
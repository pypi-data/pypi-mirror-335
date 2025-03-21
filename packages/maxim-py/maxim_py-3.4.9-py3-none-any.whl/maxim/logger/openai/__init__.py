from .utils import OpenAIUtils
from .client import MaximOpenAIClient
from .async_client import MaximOpenAIAsyncClient
from .agents import MaximOpenAIAgentsTracingProcessor

import importlib.util
if importlib.util.find_spec("openai") is None:
    raise ImportError(
        "The openai package is required. Please install it using pip: `pip install openai` or `uv add openai`"
    )

__all__ = ["OpenAIUtils", "MaximOpenAIAsyncClient", "MaximOpenAIClient","MaximOpenAIAgentsTracingProcessor"]

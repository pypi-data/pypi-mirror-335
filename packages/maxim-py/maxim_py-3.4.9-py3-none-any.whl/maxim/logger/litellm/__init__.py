import logging

logger = logging.getLogger("MaximSDK")

try:
    import litellm

    LiteLLMAvailable = True
except ImportError:
    LiteLLMAvailable = False

if not LiteLLMAvailable:
    logger.error("LiteLLM is not available. You can't use MaximLiteLLMTracer.")

from .tracer import MaximLiteLLMTracer

__all__ = ["MaximLiteLLMTracer"]

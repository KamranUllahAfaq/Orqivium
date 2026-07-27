"""Semantic convention shortcuts for Orqivium-specific spans."""

from .orqivium import OrqiviumSpanAttributes
from .gen_ai import ChainAttributes, GenAIAttributes, LLMAttributes, RetrieverAttributes, ToolAttributes

__all__ = [
    "ChainAttributes",
    "OrqiviumSpanAttributes",
    "GenAIAttributes",
    "LLMAttributes",
    "RetrieverAttributes",
    "ToolAttributes",
]

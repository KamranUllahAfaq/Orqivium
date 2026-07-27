"""Client-safe top-level exports for the Orqivium Agent package.

Default installs must be able to import ``orqivium_agent`` without pulling in server
runtime adapters or their optional dependencies. Server-only adapter entry points
remain under ``orqivium_agent.adapters.llm``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from orqivium_agent.client import Client


def __getattr__(name: str) -> object:
    if name == "Client":
        from orqivium_agent.client import Client

        return Client
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Client"]

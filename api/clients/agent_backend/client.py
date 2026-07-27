"""Synchronous API-side wrapper around the public ``orqivium-agent`` client.

``orqivium-agent`` owns the cross-service DTOs and HTTP/SSE implementation. The API
backend keeps this thin wrapper so workflow code depends on a local protocol,
gets API-native errors, and can use a deterministic fake in tests without
creating another wire contract.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Protocol

from orqivium_agent.client import (
    OrqiviumAgentClientError,
    OrqiviumAgentHTTPError,
    OrqiviumAgentStreamError,
    OrqiviumAgentTimeoutError,
    OrqiviumAgentValidationError,
)
from orqivium_agent.protocol import (
    CancelRunRequest,
    CancelRunResponse,
    CreateRunRequest,
    CreateRunResponse,
    RunEvent,
    RunStatusResponse,
)

from clients.agent_backend.errors import (
    AgentBackendError,
    AgentBackendHTTPError,
    AgentBackendStreamError,
    AgentBackendTransportError,
    AgentBackendValidationError,
)


class AgentBackendRunClient(Protocol):
    """Local boundary used by API workflow integrations to run Agent backend jobs."""

    def create_run(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create one Agent backend run and return its accepted status."""

    def cancel_run(self, run_id: str, request: CancelRunRequest | None = None) -> CancelRunResponse:
        """Request explicit cancellation for one Agent backend run."""

    def stream_events(
        self,
        run_id: str,
        *,
        after: str | None = None,
        should_stop: Callable[[], bool] | None = None,
    ) -> Iterator[RunEvent]:
        """Yield public ``orqivium-agent`` run events in stream order."""

    def wait_run(self, run_id: str, *, timeout_seconds: float | None = None) -> RunStatusResponse:
        """Wait for a run to reach a terminal status and return that status."""


class _OrqiviumAgentSyncClient(Protocol):
    """Subset of ``orqivium_agent.client.Client`` used by the API wrapper."""

    def create_run_sync(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create one run synchronously."""

    def cancel_run_sync(self, run_id: str, request: CancelRunRequest | None = None) -> CancelRunResponse:
        """Cancel one run synchronously."""

    def stream_events_sync(
        self,
        run_id: str,
        *,
        after: str | None = None,
        max_reconnects: int | None = None,
        timeout_seconds: float | None = None,
        should_stop: Callable[[], bool] | None = None,
    ) -> Iterator[RunEvent]:
        """Stream run events synchronously."""

    def wait_run_sync(self, run_id: str, *, timeout_seconds: float | None = None) -> RunStatusResponse:
        """Wait for terminal run status synchronously."""


class OrqiviumAgentBackendRunClient:
    """Adapter from API sync call sites to ``orqivium_agent.client.Client`` sync methods."""

    client: _OrqiviumAgentSyncClient

    def __init__(
        self,
        client: _OrqiviumAgentSyncClient,
        *,
        stream_max_reconnects: int = 3,
        stream_timeout_seconds: float = 1200,
    ) -> None:
        self.client = client
        self._stream_max_reconnects = stream_max_reconnects
        self._stream_timeout_seconds = stream_timeout_seconds

    def create_run(self, request: CreateRunRequest) -> CreateRunResponse:
        """Create one run through ``POST /runs`` and normalize client exceptions."""
        try:
            return self.client.create_run_sync(request)
        except Exception as exc:
            raise _normalize_orqivium_agent_error(exc) from exc

    def cancel_run(self, run_id: str, request: CancelRunRequest | None = None) -> CancelRunResponse:
        """Cancel one run through ``POST /runs/{run_id}/cancel`` and normalize exceptions."""
        try:
            return self.client.cancel_run_sync(run_id, request=request)
        except Exception as exc:
            raise _normalize_orqivium_agent_error(exc) from exc

    def stream_events(
        self,
        run_id: str,
        *,
        after: str | None = None,
        should_stop: Callable[[], bool] | None = None,
    ) -> Iterator[RunEvent]:
        """Stream run events from ``/events/sse`` with the wrapped client's reconnect policy."""
        try:
            yield from self.client.stream_events_sync(
                run_id,
                after=after,
                max_reconnects=self._stream_max_reconnects,
                timeout_seconds=self._stream_timeout_seconds,
                should_stop=should_stop,
            )
        except Exception as exc:
            raise _normalize_orqivium_agent_error(exc) from exc

    def wait_run(self, run_id: str, *, timeout_seconds: float | None = None) -> RunStatusResponse:
        """Poll run status until terminal state and normalize client exceptions."""
        try:
            return self.client.wait_run_sync(run_id, timeout_seconds=timeout_seconds)
        except Exception as exc:
            raise _normalize_orqivium_agent_error(exc) from exc


def _normalize_orqivium_agent_error(exc: Exception) -> AgentBackendError:
    """Map public ``orqivium-agent`` client errors to API-side integration errors."""
    match exc:
        case OrqiviumAgentValidationError() as error:
            return AgentBackendValidationError(
                "Agent backend request or response validation failed", detail=error.detail
            )
        case OrqiviumAgentHTTPError() as error:
            return AgentBackendHTTPError(
                f"Agent backend HTTP {error.status_code}",
                status_code=error.status_code,
                detail=error.detail,
            )
        case OrqiviumAgentTimeoutError() as error:
            return AgentBackendTransportError(str(error))
        case OrqiviumAgentStreamError() as error:
            return AgentBackendStreamError(str(error))
        case OrqiviumAgentClientError() as error:
            return AgentBackendTransportError(str(error))
        case AgentBackendError() as error:
            return error
        case _:
            return AgentBackendTransportError(str(exc) or type(exc).__name__)

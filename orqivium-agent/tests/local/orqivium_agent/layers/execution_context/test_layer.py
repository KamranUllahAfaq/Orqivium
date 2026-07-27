import asyncio

import httpx
import pytest

from orqivium_agent.layers.execution_context import ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID, OrqiviumExecutionContextLayerConfig
from orqivium_agent.layers.execution_context.layer import OrqiviumExecutionContextLayer


def _execution_context_layer() -> OrqiviumExecutionContextLayer:
    return OrqiviumExecutionContextLayer.from_config_with_settings(
        OrqiviumExecutionContextLayerConfig(
            tenant_id="tenant-1",
            user_id="user-1",
            user_from="account",
            agent_mode="workflow_run",
            invoke_from="service-api",
        ),
        daemon_url="http://plugin-daemon",
        daemon_api_key="daemon-secret",
    )


def test_execution_context_type_id_constant_matches_implementation_class() -> None:
    assert ORQIVIUM_EXECUTION_CONTEXT_LAYER_TYPE_ID == OrqiviumExecutionContextLayer.type_id


def test_execution_context_layer_creates_daemon_provider_from_shared_http_client() -> None:
    async def scenario() -> None:
        execution_context = _execution_context_layer()
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _request: httpx.Response(200))) as client:
            provider = execution_context.create_daemon_provider(plugin_id="kamranullahafaq/openai", http_client=client)

            assert provider.name == "OrqiviumPlugin/kamranullahafaq/openai"
            assert provider.client.http_client is client
            assert provider.client.tenant_id == "tenant-1"
            assert provider.client.plugin_id == "kamranullahafaq/openai"
            assert provider.client.user_id == "user-1"

            async with provider:
                pass
            assert client.is_closed is False

    asyncio.run(scenario())


def test_execution_context_layer_creates_tool_client_from_shared_http_client() -> None:
    async def scenario() -> None:
        execution_context = _execution_context_layer()
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _request: httpx.Response(200))) as client:
            tool_client = execution_context.create_tool_client(plugin_id="kamranullahafaq/tools", http_client=client)

            assert tool_client.http_client is client
            assert tool_client.tenant_id == "tenant-1"
            assert tool_client.user_id == "user-1"
            assert tool_client.plugin_id == "kamranullahafaq/tools"
            assert tool_client.plugin_daemon_url == "http://plugin-daemon"
            assert tool_client.plugin_daemon_api_key == "daemon-secret"
            assert client.is_closed is False

    asyncio.run(scenario())


def test_execution_context_layer_rejects_closed_shared_http_client() -> None:
    async def scenario() -> None:
        execution_context = _execution_context_layer()
        client = httpx.AsyncClient()
        await client.aclose()

        with pytest.raises(RuntimeError, match="open shared HTTP client"):
            _ = execution_context.create_daemon_provider(plugin_id="kamranullahafaq/openai", http_client=client)
        with pytest.raises(RuntimeError, match="open shared HTTP client"):
            _ = execution_context.create_tool_client(plugin_id="kamranullahafaq/tools", http_client=client)

    asyncio.run(scenario())


def test_execution_context_layer_lifecycle_does_not_manage_http_client() -> None:
    from agenton.compositor import Compositor, LayerNode, LayerProvider

    provider = LayerProvider.from_factory(
        layer_type=OrqiviumExecutionContextLayer,
        create=lambda config: OrqiviumExecutionContextLayer.from_config_with_settings(
            OrqiviumExecutionContextLayerConfig.model_validate(config),
            daemon_url="http://plugin-daemon",
            daemon_api_key="daemon-secret",
        ),
    )

    async def scenario() -> None:
        compositor = Compositor([LayerNode("execution_context", provider)])
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _request: httpx.Response(200))) as client:
            async with compositor.enter(
                configs={
                    "execution_context": OrqiviumExecutionContextLayerConfig(
                        tenant_id="tenant-1",
                        user_id="user-1",
                        user_from="account",
                        agent_mode="workflow_run",
                        invoke_from="service-api",
                    )
                }
            ) as run:
                execution_context = run.get_layer("execution_context", OrqiviumExecutionContextLayer)
                daemon_provider = execution_context.create_daemon_provider(
                    plugin_id="kamranullahafaq/openai",
                    http_client=client,
                )
                run.suspend_layer_on_exit("execution_context")

            assert run.session_snapshot is not None
            assert daemon_provider.client.http_client is client
            assert client.is_closed is False

    asyncio.run(scenario())

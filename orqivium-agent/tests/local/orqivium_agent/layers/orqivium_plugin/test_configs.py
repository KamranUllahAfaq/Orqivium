from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import orqivium_agent.layers.orqivium_plugin as orqivium_plugin_exports
from orqivium_agent.layers.orqivium_plugin import (
    OrqiviumPluginCredentialValue,
    OrqiviumPluginLLMLayerConfig,
    OrqiviumPluginToolCredentialType,
    OrqiviumPluginToolConfig,
    OrqiviumPluginToolParameter,
    OrqiviumPluginToolParameterForm,
    OrqiviumPluginToolParameterType,
    OrqiviumPluginToolsLayerConfig,
    OrqiviumPluginToolValue,
)


def test_orqivium_plugin_package_exports_client_safe_config_symbols_only() -> None:
    assert orqivium_plugin_exports.__all__ == [
        "ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID",
        "ORQIVIUM_PLUGIN_TOOLS_LAYER_TYPE_ID",
        "OrqiviumPluginCredentialValue",
        "OrqiviumPluginLLMLayerConfig",
        "OrqiviumPluginToolCredentialType",
        "OrqiviumPluginToolConfig",
        "OrqiviumPluginToolOption",
        "OrqiviumPluginToolParameter",
        "OrqiviumPluginToolParameterForm",
        "OrqiviumPluginToolParameterType",
        "OrqiviumPluginToolsLayerConfig",
        "OrqiviumPluginToolValue",
    ]
    assert orqivium_plugin_exports.ORQIVIUM_PLUGIN_LLM_LAYER_TYPE_ID == "orqivium.plugin.llm"
    assert orqivium_plugin_exports.ORQIVIUM_PLUGIN_TOOLS_LAYER_TYPE_ID == "orqivium.plugin.tools"
    assert not hasattr(orqivium_plugin_exports, "OrqiviumPluginLLMLayer")


def test_orqivium_plugin_llm_config_accepts_scalar_credentials_and_model_settings() -> None:
    credential: OrqiviumPluginCredentialValue = "secret"
    config = OrqiviumPluginLLMLayerConfig(
        plugin_id="kamranullahafaq/openai",
        model_provider="openai",
        model="gpt-4o-mini",
        credentials={"api_key": credential, "enabled": True, "retries": 2, "ratio": 0.5, "empty": None},
        model_settings={"temperature": 0.2, "max_tokens": 64},
    )

    assert config.plugin_id == "kamranullahafaq/openai"
    assert config.model_provider == "openai"
    assert config.credentials == {"api_key": "secret", "enabled": True, "retries": 2, "ratio": 0.5, "empty": None}
    assert config.model_settings == {"temperature": 0.2, "max_tokens": 64}
    with pytest.raises(ValidationError):
        _ = OrqiviumPluginLLMLayerConfig.model_validate(
            {
                "plugin_id": "kamranullahafaq/openai",
                "model_provider": "openai",
                "model": "gpt-4o-mini",
                "credentials": {"nested": {"not": "allowed"}},
            }
        )


def test_orqivium_plugin_llm_config_rejects_old_provider_field() -> None:
    with pytest.raises(ValidationError):
        _ = OrqiviumPluginLLMLayerConfig.model_validate(
            {
                "provider": "openai",
                "plugin_id": "kamranullahafaq/openai",
                "model": "gpt-4o-mini",
            }
        )


def test_orqivium_plugin_tools_layer_config_accepts_prepared_parameters_and_schema() -> None:
    runtime_value: OrqiviumPluginToolValue = {"locale": "en-US", "max_results": 5}
    credential_type: OrqiviumPluginToolCredentialType = "api-key"
    config = OrqiviumPluginToolsLayerConfig(
        tools=[
            OrqiviumPluginToolConfig(
                plugin_id="kamranullahafaq/tools",
                provider="search",
                tool_name="web_search",
                credential_type=credential_type,
                name="search_web",
                description="Search the web.",
                credentials={"api_key": "secret"},
                runtime_parameters={"settings": runtime_value},
                parameters=[
                    OrqiviumPluginToolParameter(
                        name="query",
                        type=OrqiviumPluginToolParameterType.STRING,
                        form=OrqiviumPluginToolParameterForm.LLM,
                        required=True,
                        llm_description="Search query",
                    )
                ],
                parameters_json_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                    },
                    "required": ["query"],
                },
            )
        ]
    )

    assert config.tools[0].plugin_id == "kamranullahafaq/tools"
    assert config.tools[0].provider == "search"
    assert config.tools[0].tool_name == "web_search"
    assert config.tools[0].credential_type == "api-key"
    assert config.tools[0].name == "search_web"
    assert config.tools[0].runtime_parameters == {"settings": {"locale": "en-US", "max_results": 5}}
    assert config.tools[0].parameters[0].name == "query"
    assert config.tools[0].parameters_json_schema["required"] == ["query"]


def test_orqivium_plugin_tool_parameter_accepts_api_tool_parameter_dump_shape() -> None:
    parameter = OrqiviumPluginToolParameter.model_validate(
        {
            "name": "query",
            "label": {"en_US": "Query"},
            "placeholder": None,
            "human_description": {"en_US": "Visible in UI"},
            "type": "select",
            "form": "llm",
            "required": True,
            "default": "orqivium",
            "llm_description": "Search query",
            "input_schema": {"type": "string"},
            "options": [
                {
                    "value": "orqivium",
                    "label": {"en_US": "Orqivium"},
                }
            ],
        }
    )

    assert parameter.name == "query"
    assert parameter.type is OrqiviumPluginToolParameterType.SELECT
    assert parameter.form is OrqiviumPluginToolParameterForm.LLM
    assert parameter.required is True
    assert parameter.default == "orqivium"
    assert parameter.input_schema == {"type": "string"}
    assert [option.value for option in parameter.options] == ["orqivium"]


def test_orqivium_plugin_tool_parameter_accepts_api_tool_parameter_attributes() -> None:
    parameter = OrqiviumPluginToolParameter.model_validate(
        SimpleNamespace(
            name="language",
            label=SimpleNamespace(en_US="Language"),
            type="string",
            form="form",
            required=False,
            default="en",
            llm_description=None,
            input_schema=None,
            options=[SimpleNamespace(value="en", label=SimpleNamespace(en_US="English"))],
        )
    )

    assert parameter.name == "language"
    assert parameter.type is OrqiviumPluginToolParameterType.STRING
    assert parameter.form is OrqiviumPluginToolParameterForm.FORM
    assert parameter.default == "en"
    assert [option.value for option in parameter.options] == ["en"]


def test_orqivium_plugin_tool_config_rejects_non_json_runtime_parameters() -> None:
    with pytest.raises(ValidationError):
        _ = OrqiviumPluginToolConfig.model_validate(
            {
                "plugin_id": "kamranullahafaq/tools",
                "provider": "search",
                "tool_name": "web_search",
                "credential_type": "api-key",
                "runtime_parameters": {"bad": object()},
            }
        )


def test_orqivium_plugin_tool_config_rejects_non_json_schema_values() -> None:
    with pytest.raises(ValidationError):
        _ = OrqiviumPluginToolConfig.model_validate(
            {
                "plugin_id": "kamranullahafaq/tools",
                "provider": "search",
                "tool_name": "web_search",
                "credential_type": "api-key",
                "parameters_json_schema": {"type": object()},
            }
        )


def test_orqivium_plugin_tool_config_rejects_strict_flag() -> None:
    with pytest.raises(ValidationError):
        _ = OrqiviumPluginToolConfig.model_validate(
            {
                "plugin_id": "kamranullahafaq/tools",
                "provider": "search",
                "tool_name": "web_search",
                "credential_type": "api-key",
                "strict": True,
            }
        )


def test_orqivium_plugin_tool_config_requires_explicit_credential_type() -> None:
    with pytest.raises(ValidationError):
        _ = OrqiviumPluginToolConfig.model_validate(
            {
                "plugin_id": "kamranullahafaq/tools",
                "provider": "search",
                "tool_name": "web_search",
            }
        )

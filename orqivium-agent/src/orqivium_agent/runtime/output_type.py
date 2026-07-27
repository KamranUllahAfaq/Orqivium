"""Validate and resolve the optional structured output layer.

Orqivium Agent keeps structured output outside Agenton's prompt/tool aggregation.
That means the request boundary must validate the public composition shape
before entering Agenton, while the entered-run helper resolves a complete output
contract containing the model-facing output type. The type itself carries the
custom Pydantic hooks needed for schema exposure and runtime validation, so the
runtime does not need a separate validator callback. Missing output layers
preserve the legacy plain-text ``str`` output contract.
"""

from typing import Protocol

from orqivium_agent.layers.output import ORQIVIUM_OUTPUT_LAYER_TYPE_ID
from orqivium_agent.layers.output.output_layer import OrqiviumOutputContract, OrqiviumOutputLayer
from orqivium_agent.protocol import ORQIVIUM_AGENT_OUTPUT_LAYER_ID
from orqivium_agent.protocol.schemas import RunComposition


class SupportsOutputLayerLookup(Protocol):
    """Minimal run surface needed to resolve the optional output layer."""

    def get_layer(self, name: str, layer_type: type[OrqiviumOutputLayer]) -> OrqiviumOutputLayer:
        """Return a typed layer instance or raise lookup/type errors."""
        ...


def validate_output_layer_composition(composition: RunComposition) -> None:
    """Reject unsupported public output-layer graph shapes.

    The proposal reserves the node name ``output`` for the single supported
    ``orqivium.output`` layer. Validating this directly from
    ``CreateRunRequest.composition.layers`` keeps bad requests from silently
    falling back to text output after entering Agenton.

    Raises:
        ValueError: If more than one ``orqivium.output`` layer is declared or if the
            single ``orqivium.output`` layer does not use the reserved node name
            ``output``.
    """
    output_layer_names = [layer.name for layer in composition.layers if layer.type == ORQIVIUM_OUTPUT_LAYER_TYPE_ID]
    if not output_layer_names:
        return

    if len(output_layer_names) > 1:
        names = ", ".join(output_layer_names)
        raise ValueError(
            f"Only one '{ORQIVIUM_OUTPUT_LAYER_TYPE_ID}' layer is supported, named '{ORQIVIUM_AGENT_OUTPUT_LAYER_ID}'. "
            f"Found layers: {names}."
        )

    output_layer_name = output_layer_names[0]
    if output_layer_name != ORQIVIUM_AGENT_OUTPUT_LAYER_ID:
        raise ValueError(
            f"Layer type '{ORQIVIUM_OUTPUT_LAYER_TYPE_ID}' must use reserved layer name "
            f"'{ORQIVIUM_AGENT_OUTPUT_LAYER_ID}', got '{output_layer_name}'."
        )


_TEXT_OUTPUT_CONTRACT = OrqiviumOutputContract(output_type=str)


def resolve_run_output_contract(run: SupportsOutputLayerLookup) -> OrqiviumOutputContract:
    """Return the run's configured pydantic-ai output contract.

    When the conventionally named output layer is absent, the runtime keeps the
    existing plain-text behavior by returning a contract whose ``output_type`` is
    ``str``. This helper assumes the
    public composition has already passed ``validate_output_layer_composition``;
    its remaining responsibility is to type-check the reserved ``output`` slot
    after compositor entry and build the validated output type from the layer
    config.

    Raises:
        TypeError: If a layer named ``output`` exists but is not a
            ``OrqiviumOutputLayer``.
        ValueError: If the output layer exists but its JSON Schema cannot be
            converted into a supported pydantic-ai structured output contract.
    """
    try:
        output_layer = run.get_layer(ORQIVIUM_AGENT_OUTPUT_LAYER_ID, OrqiviumOutputLayer)
    except KeyError:
        return _TEXT_OUTPUT_CONTRACT
    return output_layer.build_output_contract()


__all__ = [
    "OrqiviumOutputContract",
    "SupportsOutputLayerLookup",
    "resolve_run_output_contract",
    "validate_output_layer_composition",
]

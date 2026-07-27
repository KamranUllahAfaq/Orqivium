"""Client-safe exports for the Orqivium structured output layer DTOs.

The runtime layer implementation lives in ``output_layer.py`` and imports
server-side execution dependencies. Keep this package root import-safe for
client code that only needs to build run requests.
"""

from orqivium_agent.layers.output.configs import ORQIVIUM_OUTPUT_LAYER_TYPE_ID, OrqiviumOutputLayerConfig

__all__ = ["ORQIVIUM_OUTPUT_LAYER_TYPE_ID", "OrqiviumOutputLayerConfig"]

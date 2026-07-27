from typing import Literal

from pydantic import model_validator

from graphon.entities.base_node_data import BaseNodeData
from graphon.enums import BuiltinNodeTypes, NodeType


class OrqiviumAgentNodeData(BaseNodeData):
    type: NodeType = BuiltinNodeTypes.AGENT
    agent_node_kind: Literal["orqivium_agent"] = "orqivium_agent"

    @model_validator(mode="after")
    def validate_version(self) -> "OrqiviumAgentNodeData":
        if self.version != "2":
            raise ValueError("Orqivium Agent Node v2 requires version='2'")
        return self

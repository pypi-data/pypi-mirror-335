from collections.abc import Mapping
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field

from classiq.interface.debug_info import back_ref_util
from classiq.interface.generator.generated_circuit_data import (
    FunctionDebugInfoInterface,
    OperationLevel,
    StatementType,
)
from classiq.interface.model.block import Block
from classiq.interface.model.statement_block import ConcreteQuantumStatement

ParameterValue = Union[float, int, str, None]


class FunctionDebugInfo(BaseModel):
    name: str
    level: OperationLevel = Field(default=OperationLevel.UNKNOWN)
    statement_type: Union[StatementType, None] = None
    is_allocate_or_free: bool = Field(default=False)
    is_inverse: bool = Field(default=False)
    release_by_inverse: bool = Field(default=False)
    port_to_passed_variable_map: dict[str, str] = Field(default_factory=dict)
    node: Optional[ConcreteQuantumStatement] = None

    @property
    def is_allocate_or_free_(self) -> bool:
        return (
            back_ref_util.is_allocate_or_free(self.node)
            if self.node is not None
            else self.is_allocate_or_free
        )

    def update_map_from_port_mapping(self, port_mapping: Mapping[str, str]) -> None:
        new_port_to_passed_variable_map = self.port_to_passed_variable_map.copy()
        for old_key, new_key in port_mapping.items():
            if old_key in new_port_to_passed_variable_map:
                new_port_to_passed_variable_map[new_key] = (
                    new_port_to_passed_variable_map.pop(old_key)
                )
        self.port_to_passed_variable_map = new_port_to_passed_variable_map

    def update_map_from_inout_port_mapping(
        self, port_mapping: Mapping[str, tuple[str, str]]
    ) -> None:
        new_port_to_passed_variable_map = self.port_to_passed_variable_map.copy()
        for old_key, (new_key1, new_key2) in port_mapping.items():
            if old_key in new_port_to_passed_variable_map:
                value = new_port_to_passed_variable_map.pop(old_key)
                new_port_to_passed_variable_map[new_key1] = value
                new_port_to_passed_variable_map[new_key2] = value
        self.port_to_passed_variable_map = new_port_to_passed_variable_map


class DebugInfoCollection(BaseModel):
    # Pydantic only started supporting UUID as keys in Pydantic V2
    # See https://github.com/pydantic/pydantic/issues/2096#issuecomment-814860206
    # For now, we use strings as keys in the raw data and use UUID in the wrapper logic
    data: dict[str, FunctionDebugInfo] = Field(default={})
    blackbox_data: dict[str, FunctionDebugInfoInterface] = Field(default={})

    def __setitem__(self, key: UUID, value: FunctionDebugInfo) -> None:
        self.data[str(key)] = value

    def get(self, key: UUID) -> Optional[FunctionDebugInfo]:
        return self.data.get(str(key))

    def __getitem__(self, key: UUID) -> FunctionDebugInfo:
        return self.data[str(key)]

    def __contains__(self, key: UUID) -> bool:
        return str(key) in self.data

    def get_blackbox_data(self, key: UUID) -> Optional[FunctionDebugInfoInterface]:
        if (debug_info := self.get(key)) is None:
            return None
        return self.blackbox_data.get(debug_info.name)


def get_back_refs(
    debug_info: FunctionDebugInfo, collected_debug_info: DebugInfoCollection
) -> list[ConcreteQuantumStatement]:
    back_refs: list[ConcreteQuantumStatement] = []
    while (node := debug_info.node) is not None:
        #  For backwards compatibility, we make sure that the back_ref is not a block
        #  Remove this check when we start saving blocks in the debug info collection.
        assert not isinstance(node, Block)
        back_refs.insert(0, node)
        if node.back_ref is None:
            break
        next_debug_info = collected_debug_info.get(node.back_ref)
        if next_debug_info is None:
            break
        debug_info = next_debug_info
    return back_refs


def new_function_debug_info_by_node(
    node: ConcreteQuantumStatement,
) -> FunctionDebugInfo:
    return FunctionDebugInfo(
        name="",
        parameters=dict(),
        level=OperationLevel.QMOD_STATEMENT,
        node=node._as_back_ref(),
    )

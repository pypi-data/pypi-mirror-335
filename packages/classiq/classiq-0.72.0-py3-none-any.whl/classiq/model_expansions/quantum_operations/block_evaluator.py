from collections.abc import Sequence
from typing import TYPE_CHECKING

from classiq.interface.model.quantum_function_declaration import PositionalArg
from classiq.interface.model.quantum_statement import QuantumOperation, QuantumStatement

from classiq.model_expansions.closure import Closure
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import Scope

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.base_interpreter import BaseInterpreter


_BLOCK_RENAMES = {
    "compute": "within",
    "action": "apply",
}
_REVERSE_BLOCK_RENAMES = {rename: name for name, rename in _BLOCK_RENAMES.items()}


class BlockEvaluator(Emitter[QuantumOperation]):
    def __init__(
        self, interpreter: "BaseInterpreter", operation_name: str, *block_names: str
    ) -> None:
        super().__init__(interpreter)
        self._operation_name = operation_name
        self._block_names: Sequence[str] = block_names

    def emit(self, op: QuantumOperation, /) -> bool:
        expanded_blocks: dict[str, list[QuantumStatement]] = {}
        blocks = [
            block
            for block in self._block_names
            if hasattr(op, block) and getattr(op, block) is not None
        ]

        if len(blocks) > 0:
            if op.is_generative():
                expanded_blocks = self.expand_generative_blocks(op)
            else:
                expanded_blocks = self.expand_blocks(op, blocks)
            expanded_blocks.update(expanded_blocks)

        op = op.model_copy(update={**expanded_blocks, "back_ref": op.uuid})
        self._builder.emit_statement(op)
        return True

    def expand_blocks(
        self, op: QuantumOperation, block_names: list[str]
    ) -> dict[str, list[QuantumStatement]]:
        blocks = {
            _BLOCK_RENAMES.get(block, block): getattr(op, block)
            for block in block_names
        }
        block_closure = Closure(
            name=self._operation_name,
            scope=self.get_scope(op),
            positional_arg_declarations=self.get_params(op),
            blocks=blocks,
        )
        context = self._expand_operation(block_closure)
        return {
            block: context.statements(_BLOCK_RENAMES.get(block, block))
            for block in block_names
        }

    def expand_generative_blocks(
        self, op: QuantumOperation
    ) -> dict[str, list[QuantumStatement]]:
        blocks = [
            block for block in self._block_names if op.has_generative_block(block)
        ]
        context = self._expand_generative_context(
            op,
            self._operation_name,
            blocks,
            self.get_params(op),
            self.get_scope(op),
        )
        return {
            _REVERSE_BLOCK_RENAMES.get(block, block): context.statements(block)
            for block in blocks
        }

    def get_params(self, op: QuantumOperation) -> Sequence[PositionalArg]:
        return []

    def get_scope(self, op: QuantumOperation) -> Scope:
        return Scope(parent=self._current_scope)

from classiq.interface.debug_info.debug_info import FunctionDebugInfo
from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.generated_circuit_data import OperationLevel
from classiq.interface.model.allocate import Allocate
from classiq.interface.model.handle_binding import NestedHandleBinding
from classiq.interface.model.quantum_type import QuantumBitvector

from classiq.model_expansions.evaluators.quantum_type_utils import copy_type_information
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import QuantumSymbol


class AllocateEmitter(Emitter[Allocate]):
    def emit(self, allocate: Allocate, /) -> bool:
        target: QuantumSymbol = self._interpreter.evaluate(allocate.target).as_type(
            QuantumSymbol
        )

        if isinstance(target.handle, NestedHandleBinding):
            raise ClassiqValueError(
                f"Cannot allocate partial quantum variable {str(target.handle)!r}"
            )

        size = self._get_var_size(target, allocate.size)
        allocate = allocate.model_copy(
            update=dict(
                size=Expression(expr=str(size)),
                target=target.handle,
                back_ref=allocate.uuid,
            )
        )
        self._register_debug_info(allocate)
        self.emit_statement(allocate)
        return True

    def _get_var_size(self, target: QuantumSymbol, size: Expression | None) -> int:
        if size is None:
            if not target.quantum_type.is_evaluated:
                raise ClassiqValueError(
                    f"Could not infer the size of variable {str(target.handle)!r}"
                )
            return target.quantum_type.size_in_bits

        size_value = self._interpreter.evaluate(size).value
        if not isinstance(size_value, (int, float)):
            raise ClassiqValueError(
                f"The number of allocated qubits must be an integer. Got "
                f"{str(size_value)!r}"
            )
        size_value = int(size_value)
        copy_type_information(
            QuantumBitvector(length=Expression(expr=str(size_value))),
            target.quantum_type,
            str(target.handle),
        )
        return size_value

    def _register_debug_info(self, allocate: Allocate) -> None:
        if (
            allocate.uuid in self._debug_info
            and self._debug_info[allocate.uuid].name != ""
        ):
            return
        parameters: dict[str, str] = {}
        if allocate.size is not None:
            parameters["num_qubits"] = allocate.size.expr
        self._debug_info[allocate.uuid] = FunctionDebugInfo(
            name="allocate",
            parameters=parameters,
            level=OperationLevel.QMOD_STATEMENT,
            is_allocate_or_free=True,
            port_to_passed_variable_map={"ARG": str(allocate.target)},
            node=allocate._as_back_ref(),
        )

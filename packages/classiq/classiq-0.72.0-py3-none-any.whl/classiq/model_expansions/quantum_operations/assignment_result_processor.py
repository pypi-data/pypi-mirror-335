from classiq.interface.generator.arith.arithmetic import compute_arithmetic_result_type
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
    ArithmeticOperationKind,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumAssignmentOperation,
)

from classiq.model_expansions.evaluators.quantum_type_utils import copy_type_information
from classiq.model_expansions.quantum_operations.arithmetic.explicit_boolean_expressions import (
    convert_assignment_bool_expression,
    validate_assignment_bool_expression,
)
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import QuantumSymbol
from classiq.model_expansions.transformers.ast_renamer import rename_variables


class AssignmentResultProcessor(Emitter[QuantumAssignmentOperation]):
    def emit(self, op: QuantumAssignmentOperation, /) -> bool:
        if (
            isinstance(op, ArithmeticOperation)
            and op.operation_kind == ArithmeticOperationKind.Assignment
        ):
            direction = PortDeclarationDirection.Output
            self._update_result_type(op)
            convert_assignment_bool_expression(op)
        else:
            direction = PortDeclarationDirection.Inout
        self._capture_handle(op.result_var, direction)
        return False

    def _update_result_type(self, op: ArithmeticOperation) -> None:
        expr = self._evaluate_expression(op.expression)
        symbols = self._get_symbols_in_expression(expr)
        expr_str = rename_variables(
            expr.expr,
            {str(symbol.handle): symbol.handle.identifier for symbol in symbols}
            | {symbol.handle.qmod_expr: symbol.handle.identifier for symbol in symbols},
        )
        for symbol in symbols:
            expr_str = expr_str.replace(
                symbol.handle.qmod_expr, symbol.handle.identifier
            )
        result_type = compute_arithmetic_result_type(
            expr_str,
            {symbol.handle.identifier: symbol.quantum_type for symbol in symbols},
            self._machine_precision,
        )
        result_symbol = self._interpreter.evaluate(op.result_var).as_type(QuantumSymbol)

        validate_assignment_bool_expression(
            result_symbol, op.expression.expr, op.operation_kind
        )  # must be here, otherwise copy_type_information will throw a non-indicative error
        copy_type_information(
            result_type, result_symbol.quantum_type, str(op.result_var)
        )

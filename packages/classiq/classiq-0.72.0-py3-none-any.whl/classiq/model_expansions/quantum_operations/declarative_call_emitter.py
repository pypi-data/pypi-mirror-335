from itertools import chain
from typing import TYPE_CHECKING, Generic

from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.port_declaration import PortDeclaration

from classiq.model_expansions.closure import FunctionClosure, GenerativeClosure
from classiq.model_expansions.quantum_operations.call_emitter import CallEmitter
from classiq.model_expansions.quantum_operations.emitter import QuantumStatementT
from classiq.model_expansions.scope import Evaluated
from classiq.qmod.model_state_container import QMODULE

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.frontend_generative_interpreter import (
        FrontendGenerativeInterpreter,
    )


class DeclarativeCallEmitter(
    Generic[QuantumStatementT], CallEmitter[QuantumStatementT]
):
    _interpreter: "FrontendGenerativeInterpreter"

    def __init__(self, interpreter: "FrontendGenerativeInterpreter") -> None:
        super().__init__(interpreter)

    def should_expand_function(
        self, function: FunctionClosure, args: list[Evaluated]
    ) -> bool:
        if not super().should_expand_function(function, args):
            return False

        if self._is_function_purely_declarative(
            function
        ) and self._are_args_purely_declarative(args):
            self._interpreter.add_purely_declarative_function(function)
            return False

        return True

    def _is_function_purely_declarative(self, function: FunctionClosure) -> bool:
        if function.name not in QMODULE.native_defs:
            return False

        if isinstance(function, GenerativeClosure):
            return False

        if any(
            not param.quantum_type.is_instantiated
            for param in function.positional_arg_declarations
            if isinstance(param, PortDeclaration)
            and param.direction == PortDeclarationDirection.Output
        ):
            return False

        dependencies = QMODULE.function_dependencies[function.name]
        return self._are_identifiers_purely_declarative(dependencies)

    def _are_args_purely_declarative(self, args: list[Evaluated]) -> bool:
        values = [arg.value for arg in args]
        function_inputs: list[FunctionClosure] = list(
            chain.from_iterable(
                (
                    [arg]
                    if isinstance(arg, FunctionClosure)
                    else (
                        arg
                        if isinstance(arg, list)
                        and any(isinstance(item, FunctionClosure) for item in arg)
                        else []
                    )
                )
                for arg in values
            )
        )
        if any(func.is_lambda for func in function_inputs):
            return False
        dependencies = [func.name for func in function_inputs if not func.is_lambda]
        return self._are_identifiers_purely_declarative(dependencies)

    def _are_identifiers_purely_declarative(self, dependencies: list[str]) -> bool:
        return not any(
            isinstance(self._current_scope[dep].value, GenerativeClosure)
            for dep in dependencies
        )

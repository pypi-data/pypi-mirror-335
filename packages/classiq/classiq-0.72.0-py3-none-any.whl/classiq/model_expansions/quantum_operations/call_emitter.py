from collections.abc import Sequence
from itertools import chain, combinations
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    cast,
)
from uuid import UUID

import sympy

from classiq.interface.debug_info.debug_info import FunctionDebugInfo
from classiq.interface.exceptions import ClassiqExpansionError
from classiq.interface.generator.expressions.proxies.classical.any_classical_value import (
    AnyClassicalValue,
)
from classiq.interface.generator.expressions.proxies.classical.classical_proxy import (
    ClassicalProxy,
)
from classiq.interface.generator.expressions.proxies.classical.qmod_struct_instance import (
    QmodStructInstance,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.generated_circuit_data import OperationLevel
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.native_function_definition import NativeFunctionDefinition
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_call import ArgValue, QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    NamedParamsQuantumFunctionDeclaration,
    PositionalArg,
)
from classiq.interface.model.quantum_statement import QuantumStatement
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq.model_expansions.capturing.captured_vars import (
    INITIALIZED_VAR_MESSAGE,
    UNINITIALIZED_VAR_MESSAGE,
    validate_args_are_not_propagated,
)
from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.evaluators.argument_types import (
    add_information_from_output_arguments,
)
from classiq.model_expansions.evaluators.parameter_types import (
    evaluate_parameter_types_from_args,
)
from classiq.model_expansions.function_builder import (
    FunctionContext,
)
from classiq.model_expansions.quantum_operations.emitter import (
    Emitter,
    QuantumStatementT,
)
from classiq.model_expansions.scope import Evaluated, QuantumSymbol, Scope
from classiq.model_expansions.transformers.var_splitter import VarSplitter
from classiq.qmod.builtins.functions import free
from classiq.qmod.semantics.validation.signature_validation import (
    validate_function_signature,
)

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.base_interpreter import BaseInterpreter


def _validate_cloning(evaluated_args: list[Evaluated]) -> None:
    handles = [
        arg.value.handle
        for arg in evaluated_args
        if isinstance(arg.value, QuantumSymbol)
    ]
    for handle, other_handle in combinations(handles, 2):
        if handle.overlaps(other_handle):
            if handle == other_handle:
                raise ClassiqExpansionError(
                    f"Quantum cloning violation: Argument {str(handle)!r} is "
                    f"duplicated"
                )
            raise ClassiqExpansionError(
                f"Quantum cloning violation: Arguments {str(handle)!r} and "
                f"{str(other_handle)!r} overlap"
            )


def _is_symbolic(arg: Any) -> bool:
    if isinstance(arg, list):
        return any(_is_symbolic(item) for item in arg)
    if isinstance(arg, QmodStructInstance):
        return any(_is_symbolic(item) for item in arg.fields.values())
    if isinstance(arg, sympy.Basic):
        return len(arg.free_symbols) > 0
    return isinstance(arg, (ClassicalProxy, AnyClassicalValue))


class CallEmitter(Generic[QuantumStatementT], Emitter[QuantumStatementT], VarSplitter):
    def __init__(self, interpreter: "BaseInterpreter") -> None:
        Emitter.__init__(self, interpreter)
        VarSplitter.__init__(self, interpreter._builder.current_scope)

    @staticmethod
    def _should_wrap(body: Sequence[QuantumStatement]) -> bool:
        # This protects shadowing of captured variables (i.e, bad user code) by wrapping the body in a function
        # I'm sure there are better ways to handle it, but this is the simplest way to do it for now
        return any(isinstance(stmt, VariableDeclarationStatement) for stmt in body)

    def _create_expanded_wrapping_function(
        self, name: str, body: Sequence[QuantumStatement]
    ) -> QuantumFunctionCall:
        wrapping_function = FunctionClosure.create(
            name=self._counted_name_allocator.allocate(name),
            body=body,
            scope=Scope(parent=self._current_scope),
            lambda_external_vars=self._builder.current_block.captured_vars,
        )
        return self._create_quantum_function_call(wrapping_function, list(), None)

    def _emit_quantum_function_call(
        self,
        function: FunctionClosure,
        args: list[ArgValue],
        propagated_debug_info: FunctionDebugInfo | None,
    ) -> QuantumFunctionCall:
        call = self._create_quantum_function_call(
            function, args, propagated_debug_info=propagated_debug_info
        )
        self.emit_statement(call)
        return call

    @staticmethod
    def _get_back_ref(
        propagated_debug_info: FunctionDebugInfo | None,
    ) -> UUID | None:
        if propagated_debug_info is None:
            return None
        if propagated_debug_info.node is None:
            return None
        return propagated_debug_info.node.uuid

    def _create_quantum_function_call(
        self,
        function: FunctionClosure,
        args: list[ArgValue],
        propagated_debug_info: FunctionDebugInfo | None,
    ) -> QuantumFunctionCall:
        function = function.clone()
        function = function.set_depth(self._builder.current_function.depth + 1)
        self._validate_call_args(function.positional_arg_declarations, args)
        evaluated_args = [self._interpreter.evaluate(arg) for arg in args]
        _validate_cloning(evaluated_args)
        new_declaration = self._prepare_fully_typed_declaration(
            function, evaluated_args
        )
        new_positional_arg_decls = new_declaration.positional_arg_declarations
        if not self.should_expand_function(function, evaluated_args):
            is_atomic = True
            new_declaration = self._expanded_functions_by_name.get(
                function.name, new_declaration
            )
        else:
            is_atomic = False
            new_declaration = self._expand_function(
                evaluated_args, new_declaration, function
            )

        new_positional_args = self._get_new_positional_args(
            evaluated_args, is_atomic, new_positional_arg_decls
        )
        captured_args = function.captured_vars.filter_vars(function).get_captured_args(
            self._builder.current_function
        )
        validate_args_are_not_propagated(new_positional_args, captured_args)
        new_positional_args.extend(captured_args)
        new_call = QuantumFunctionCall(
            function=new_declaration.name,
            positional_args=new_positional_args,
            back_ref=self._get_back_ref(propagated_debug_info),
        )
        is_allocate_or_free = new_call.func_name == free.func_decl.name

        port_to_passed_variable_map = {
            arg_decl.name: str(evaluated_arg.value.handle)
            for arg_decl, evaluated_arg in zip(new_positional_arg_decls, evaluated_args)
            if isinstance(arg_decl, PortDeclaration)
        }
        self._debug_info[new_call.uuid] = FunctionDebugInfo(
            name=new_call.func_name,
            level=OperationLevel.QMOD_FUNCTION_CALL,
            is_allocate_or_free=is_allocate_or_free,
            port_to_passed_variable_map=port_to_passed_variable_map,
            node=new_call._as_back_ref(),
        )
        new_call.set_func_decl(new_declaration)
        return new_call

    def should_expand_function(
        self, function: FunctionClosure, args: list[Evaluated]
    ) -> bool:
        return not function.is_atomic

    def _expand_function(
        self,
        args: list[Evaluated],
        decl: NamedParamsQuantumFunctionDeclaration,
        function: FunctionClosure,
    ) -> NamedParamsQuantumFunctionDeclaration:
        self._add_params_to_scope(decl.positional_arg_declarations, args, function)
        context = self._expand_operation(function.with_new_declaration(decl))
        function_context = cast(FunctionContext, context)
        closure_id = function_context.closure.closure_id
        if closure_id in self._expanded_functions:
            function_def = self._expanded_functions[closure_id]
            self._expanded_functions_compilation_metadata[
                function_def.name
            ].occurrences_number += 1
            return function_def

        function_def = self._create_function_definition(function_context, args)
        self._expanded_functions[closure_id] = function_def
        self._top_level_scope[function_def.name] = Evaluated(
            value=function_context.closure.with_new_declaration(function_def)
        )
        compilation_metadata = self._functions_compilation_metadata.get(function.name)
        if compilation_metadata is not None:
            self._expanded_functions_compilation_metadata[function_def.name] = (
                compilation_metadata
            )
        return function_def

    def _create_function_definition(
        self, function_context: FunctionContext, args: list[Evaluated]
    ) -> NativeFunctionDefinition:
        params = [
            param
            for arg, param in zip(args, function_context.positional_arg_declarations)
            if isinstance(param, PortDeclaration)
            or (
                isinstance(param, ClassicalParameterDeclaration)
                and _is_symbolic(arg.value)
            )
        ]
        func_def = self._builder.create_definition(function_context, params)

        captured_vars = function_context.closure.captured_vars.filter_vars(
            function_context.closure
        )
        captured_ports = captured_vars.get_captured_parameters()
        if len(captured_ports) == 0:
            return func_def
        func_def.positional_arg_declarations = list(
            chain.from_iterable((func_def.positional_arg_declarations, captured_ports))
        )

        if not function_context.is_lambda:
            return func_def
        func_def.body = self.rewrite(
            func_def.body, captured_vars.get_captured_mapping()
        )

        return func_def

    @staticmethod
    def _add_params_to_scope(
        parameters: Sequence[PositionalArg],
        arguments: Sequence[Evaluated],
        closure: FunctionClosure,
    ) -> None:
        for parameter, argument in zip(parameters, arguments):
            param_handle = HandleBinding(name=parameter.name)
            if isinstance(argument.value, QuantumSymbol):
                assert isinstance(parameter, PortDeclaration)
                closure.scope[parameter.name] = Evaluated(
                    QuantumSymbol(
                        handle=param_handle,
                        quantum_type=parameter.quantum_type,
                    ),
                    defining_function=closure,
                )
            elif _is_symbolic(argument.value):
                assert isinstance(parameter, ClassicalParameterDeclaration)
                closure.scope[parameter.name] = Evaluated(
                    value=parameter.classical_type.get_classical_proxy(param_handle),
                    defining_function=closure,
                )
            else:
                closure.scope[parameter.name] = argument

    def _get_new_positional_args(
        self,
        evaluated_args: list[Evaluated],
        is_atomic: bool,
        new_positional_arg_decls: Sequence[PositionalArg],
    ) -> list[ArgValue]:
        evaluated_args = add_information_from_output_arguments(
            new_positional_arg_decls, evaluated_args
        )
        if is_atomic:
            return [arg.emit() for arg in evaluated_args]

        positional_args = [
            arg.emit()
            for arg in evaluated_args
            if isinstance(arg.value, QuantumSymbol) or _is_symbolic(arg.value)
        ]

        return positional_args

    def _prepare_fully_typed_declaration(
        self, function: FunctionClosure, evaluated_args: list[Evaluated]
    ) -> NamedParamsQuantumFunctionDeclaration:
        """
        Given, for example,
        def my_func(x: int, q: QArray["x"], p: QArray[]) -> None:
        ...
        def main(...):
            ...
            allocate(5, s)
            my_func(3, r, s)
        The code below will evaluate x to be 3, q to be of size 3 and p to be of size 5.
        Note that it requires a scope for the parameter declaration space, which is
        different from the call scope. For example, the former uses r,s and the latter
        uses p, q.
        """
        validate_function_signature(function.positional_arg_declarations)
        # The signature scope is passed as a separate argument to avoid contaminating the statement execution scope
        return NamedParamsQuantumFunctionDeclaration(
            name=function.name,
            positional_arg_declarations=evaluate_parameter_types_from_args(
                function,
                function.signature_scope,
                evaluated_args,
            ),
        )

    def _validate_call_args(
        self, params: Sequence[PositionalArg], args: list[ArgValue]
    ) -> None:
        for param, arg in zip(params, args):
            if not isinstance(param, PortDeclaration) or not isinstance(
                arg, HandleBinding
            ):
                continue
            var_name = arg.name
            symbol = self._interpreter.evaluate(var_name)
            if (
                not isinstance(symbol.value, QuantumSymbol)
                or symbol.defining_function is None
            ):
                continue
            var_state = self._builder.current_block.captured_vars.get_state(
                var_name, symbol.defining_function
            )
            if not var_state and param.direction in (
                PortDeclarationDirection.Inout,
                PortDeclarationDirection.Input,
            ):
                raise ClassiqExpansionError(UNINITIALIZED_VAR_MESSAGE.format(var_name))
            if var_state and param.direction == PortDeclarationDirection.Output:
                raise ClassiqExpansionError(INITIALIZED_VAR_MESSAGE.format(var_name))

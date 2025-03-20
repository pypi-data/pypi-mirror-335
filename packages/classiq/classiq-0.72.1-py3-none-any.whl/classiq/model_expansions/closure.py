import dataclasses
import json
from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any, Optional

from typing_extensions import Self

from classiq.interface.exceptions import ClassiqInternalExpansionError
from classiq.interface.model.quantum_function_declaration import (
    NamedParamsQuantumFunctionDeclaration,
    PositionalArg,
)
from classiq.interface.model.quantum_lambda_function import QuantumCallable
from classiq.interface.model.quantum_statement import QuantumStatement

from classiq.model_expansions.capturing.captured_vars import CapturedVars
from classiq.model_expansions.scope import (
    Evaluated,
    QuantumSymbol,
    Scope,
    evaluated_to_str as evaluated_classical_param_to_str,
)
from classiq.qmod.builtins.functions import permute
from classiq.qmod.quantum_function import GenerativeQFunc


@dataclass(frozen=True)
class Closure:
    name: str
    blocks: dict[str, Sequence[QuantumStatement]]
    scope: Scope
    positional_arg_declarations: Sequence[PositionalArg] = tuple()
    captured_vars: CapturedVars = field(default_factory=CapturedVars)


@dataclass(frozen=True)
class GenerativeClosure(Closure):
    generative_blocks: dict[str, GenerativeQFunc] = None  # type:ignore[assignment]


@dataclass(frozen=True)
class FunctionClosure(Closure):
    is_lambda: bool = False
    is_atomic: bool = False
    signature_scope: Scope = field(default_factory=Scope)
    _depth: Optional[int] = None

    @property
    def depth(self) -> int:
        if self._depth is None:
            raise ClassiqInternalExpansionError
        return self._depth

    # creates a unique id for the function closure based on the arguments values.
    # The closure is changing across the interpreter flow so it's closure_id may change
    @property
    def closure_id(self) -> str:
        signature = _generate_closure_id(self.scope.data.values())
        return f"{self.name}__{signature}"

    @property
    def body(self) -> Sequence[QuantumStatement]:
        if self.name == permute.func_decl.name:
            # permute is an old Qmod "generative" function that doesn't have a body
            return []
        return self.blocks["body"]

    @classmethod
    def create(
        cls,
        name: str,
        scope: Scope,
        body: Optional[Sequence[QuantumStatement]] = None,
        positional_arg_declarations: Sequence[PositionalArg] = tuple(),
        lambda_external_vars: Optional[CapturedVars] = None,
        is_atomic: bool = False,
        **kwargs: Any,
    ) -> Self:
        blocks = {"body": body} if body is not None else {}
        captured_vars = CapturedVars()
        if lambda_external_vars is not None:
            captured_vars.set_parent(lambda_external_vars)
        return cls(
            name,
            blocks,
            scope,
            positional_arg_declarations,
            captured_vars,
            lambda_external_vars is not None,
            is_atomic,
            **kwargs,
        )

    def with_new_declaration(
        self, declaration: NamedParamsQuantumFunctionDeclaration
    ) -> Self:
        fields: dict = self.__dict__ | {
            "name": declaration.name,
            "positional_arg_declarations": declaration.positional_arg_declarations,
        }
        return type(self)(**fields)

    def set_depth(self, depth: int) -> Self:
        return dataclasses.replace(self, _depth=depth)

    def clone(self) -> Self:
        return dataclasses.replace(
            self,
            scope=self.scope.clone(),
            signature_scope=self.signature_scope.clone(),
            captured_vars=self.captured_vars.clone(),
        )

    def emit(self) -> QuantumCallable:
        return self.name


@dataclass(frozen=True)
class GenerativeFunctionClosure(GenerativeClosure, FunctionClosure):
    pass


def _generate_closure_id(evaluated_args: Collection[Evaluated]) -> str:
    args_signature = [
        _evaluated_arg_to_str(eval_arg.value) for eval_arg in evaluated_args
    ]
    return json.dumps(args_signature)


@singledispatch
def _evaluated_arg_to_str(arg: Any) -> str:
    if isinstance(arg, str):
        return arg
    if isinstance(arg, QuantumSymbol):
        return _evaluated_quantum_symbol_to_str(arg)
    if isinstance(arg, FunctionClosure):
        return _evaluated_one_operand_to_str(arg)
    if isinstance(arg, list) and arg and isinstance(arg[0], FunctionClosure):
        return _evaluated_operands_list_to_str(arg)
    return evaluated_classical_param_to_str(arg)


def _evaluated_quantum_symbol_to_str(port: QuantumSymbol) -> str:
    return port.quantum_type.model_dump_json(exclude_none=True, exclude={"name"})


def _evaluated_one_operand_to_str(operand: FunctionClosure) -> str:
    return operand.closure_id


def _evaluated_operands_list_to_str(arg: list[FunctionClosure]) -> str:
    return json.dumps([_evaluated_one_operand_to_str(ope) for ope in arg])

from collections.abc import Mapping
from enum import Enum
from typing import Any, Callable, Union, get_args

from sympy import Eq, Expr, Piecewise, Symbol

from classiq.interface.exceptions import (
    ClassiqExpansionError,
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.expressions.expression_types import (
    ExpressionValue,
    QmodStructInstance,
)
from classiq.interface.generator.expressions.proxies.classical.any_classical_value import (
    AnyClassicalValue,
)
from classiq.interface.generator.expressions.proxies.quantum.qmod_qscalar_proxy import (
    QmodQNumProxy,
)
from classiq.interface.generator.expressions.proxies.quantum.qmod_qstruct_proxy import (
    QmodQStructProxy,
)
from classiq.interface.generator.expressions.proxies.quantum.qmod_sized_proxy import (
    QmodSizedProxy,
)
from classiq.interface.generator.expressions.type_proxy import TypeProxy
from classiq.interface.generator.functions.classical_function_declaration import (
    ClassicalFunctionDeclaration,
)
from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalArray,
    ClassicalList,
    ClassicalType,
    OpaqueHandle,
    QmodPyObject,
    Real,
    StructMetaType,
)
from classiq.interface.generator.functions.type_name import TypeName

from classiq.model_expansions.model_tables import (
    HandleIdentifier,
    HandleTable,
)
from classiq.model_expansions.sympy_conversion.arithmetics import (
    BitwiseAnd,
    BitwiseNot,
    BitwiseOr,
    BitwiseXor,
    LogicalXor,
)
from classiq.model_expansions.sympy_conversion.expression_to_sympy import (
    MISSING_SLICE_VALUE_PLACEHOLDER,
)
from classiq.model_expansions.sympy_conversion.sympy_to_python import (
    sympy_to_python,
)
from classiq.model_expansions.utils.sympy_utils import (
    is_constant_subscript,
    unwrap_sympy_numeric,
)
from classiq.qmod.model_state_container import QMODULE


def qmod_val_to_python(val: ExpressionValue, qmod_type: ClassicalType) -> Any:
    if isinstance(qmod_type, TypeName):
        if (
            isinstance(val, QmodStructInstance)
            and val.struct_declaration == QMODULE.type_decls[qmod_type.name]
        ):
            return {
                field_name: qmod_val_to_python(val.fields[field_name], field_type)
                for field_name, field_type in val.struct_declaration.variables.items()
            }

        if isinstance(val, (Enum, int)):
            return val

    elif isinstance(qmod_type, (ClassicalArray, ClassicalList)):
        if isinstance(val, list):
            return [qmod_val_to_python(elem, qmod_type.element_type) for elem in val]

    elif isinstance(qmod_type, OpaqueHandle):
        if isinstance(val, HandleIdentifier):
            return HandleTable.get_handle_object(val)

    elif isinstance(val, Expr):
        return sympy_to_python(val)

    elif isinstance(qmod_type, Real):
        if isinstance(val, (float, int)):
            return val

    elif isinstance(qmod_type, Bool):
        if isinstance(val, bool):
            return val

    elif isinstance(qmod_type, StructMetaType):
        if isinstance(val, TypeProxy):
            return val.struct_declaration

    elif isinstance(val, int):  # other scalars are represented as int
        return val

    raise ClassiqInternalExpansionError(
        f"Bad value {val!r} of type {type(val)!r} for {qmod_type!r}"
    )


def python_val_to_qmod(val: Any, qmod_type: ClassicalType) -> ExpressionValue:
    if isinstance(qmod_type, TypeName):
        if qmod_type.name in QMODULE.enum_decls:
            return val

        struct_decl = QMODULE.type_decls[qmod_type.name]
        if not isinstance(val, Mapping):
            raise ClassiqInternalExpansionError(
                f"Bad value for struct {struct_decl.name}"
            )
        qmod_dict = {
            field_name: python_val_to_qmod(val[field_name], field_type)
            for field_name, field_type in struct_decl.variables.items()
        }
        return QmodStructInstance(struct_decl, qmod_dict)

    if isinstance(qmod_type, ClassicalList):
        if not isinstance(val, list):
            raise ClassiqInternalExpansionError("Bad value for list")
        return [python_val_to_qmod(elem, qmod_type.element_type) for elem in val]

    if isinstance(qmod_type, OpaqueHandle):
        if not isinstance(val, QmodPyObject):
            raise ClassiqInternalExpansionError("Bad value opaque handle")
        return HandleTable.set_handle_object(val)

    return val


def python_call_wrapper(func: Callable, *args: ExpressionValue) -> Any:
    func_decl = ClassicalFunctionDeclaration.FOREIGN_FUNCTION_DECLARATIONS[
        func.__name__
    ]
    python_args = [
        qmod_val_to_python(args[idx], param_type.classical_type)
        for idx, param_type in enumerate(func_decl.param_decls)
    ]
    assert func_decl.return_type is not None
    return python_val_to_qmod(func(*python_args), func_decl.return_type)


def struct_literal(struct_type_symbol: Symbol, **kwargs: Any) -> QmodStructInstance:
    return QmodStructInstance(
        QMODULE.type_decls[struct_type_symbol.name],
        {field: sympy_to_python(field_value) for field, field_value in kwargs.items()},
    )


def get_field(
    proxy: Union[
        QmodSizedProxy, QmodStructInstance, QmodQStructProxy, list, AnyClassicalValue
    ],
    field: str,
) -> ExpressionValue:
    if isinstance(proxy, AnyClassicalValue):
        return AnyClassicalValue(f"({proxy}).{field}")
    if isinstance(proxy, type) and issubclass(proxy, Enum):
        return getattr(proxy, field)
    if isinstance(proxy, Symbol) and not isinstance(proxy, QmodSizedProxy):
        raise ClassiqExpansionError(
            f"Cannot evaluate '{proxy}.{field}': Variable {str(proxy)!r} is not "
            f"initialized"
        )
    if isinstance(proxy, list):
        if field != "len":
            raise ClassiqExpansionError(
                f"List {str(proxy)!r} has no attribute {field!r}. "
                f"Available attributes: len"
            )
        return len(proxy)
    if field not in proxy.fields:
        if isinstance(proxy, (QmodStructInstance, QmodQStructProxy)):
            property_name = "field"
        else:
            property_name = "attribute"
        suffix = (
            f". Available {property_name}s: {', '.join(proxy.fields.keys())}"
            if len(proxy.fields) > 0
            else ""
        )
        proxy_str = proxy.__name__ if isinstance(proxy, type) else f"{str(proxy)!r}"
        raise ClassiqExpansionError(
            f"{proxy.type_name} {proxy_str} has no {property_name} {field!r}{suffix}"
        )
    return proxy.fields[field]


def get_type(struct_type: Symbol) -> TypeProxy:
    return TypeProxy(QMODULE.type_decls[struct_type.name])


def do_div(lhs: Any, rhs: Any) -> Any:
    lhs = unwrap_sympy_numeric(lhs)
    rhs = unwrap_sympy_numeric(rhs)
    return lhs / rhs


_EXPRESSION_TYPES = get_args(ExpressionValue)


def _is_qmod_value(val: Any) -> bool:
    if not isinstance(val, slice):
        return isinstance(val, _EXPRESSION_TYPES)
    if val.start is not None and not isinstance(val.start, _EXPRESSION_TYPES):
        return False
    if val.stop is not None and not isinstance(val.stop, _EXPRESSION_TYPES):
        return False
    return val.step is None or isinstance(val.step, _EXPRESSION_TYPES)


def do_subscript(value: Any, index: Any) -> Any:
    if not isinstance(value, list) or not isinstance(index, QmodQNumProxy):
        if isinstance(index, (QmodSizedProxy, QmodStructInstance)):
            raise ClassiqExpansionError(
                f"Subscript {value}[{index}] is not supported. Supported subscripts "
                f"include:\n"
                f"\t1. `qbv[idx]`, where `qbv` is a quantum array and `idx` is a "
                f"classical integer.\n"
                f"\t2. `l[n]`, where `l` is a list of classical real numbers and `n` "
                f"is a classical or quantum integer."
            )
        if (
            isinstance(value, list)
            and not is_constant_subscript(index)
            and _is_qmod_value(index)
        ):
            return AnyClassicalValue(str(value))[index]
        return value[index]
    if index.is_signed or index.fraction_digits > 0:
        raise ClassiqExpansionError(
            "Quantum numeric subscript must be an unsigned integer (is_signed=False, "
            "fraction_digits=0)"
        )
    if len(value) != 2**index.size:
        raise ClassiqExpansionError(
            f"Quantum numeric subscript size mismatch: The quantum numeric has "
            f"{index.size} qubits but the list size is {len(value)} != 2**{index.size}"
        )
    return Piecewise(
        *[(item, Eq(index, idx)) for idx, item in enumerate(value[:-1])],
        (value[-1], True),
    )


def do_slice(value: Any, lower: Any, upper: Any) -> Any:
    if isinstance(lower, Symbol) and str(lower) == MISSING_SLICE_VALUE_PLACEHOLDER:
        lower = None
    if isinstance(upper, Symbol) and str(upper) == MISSING_SLICE_VALUE_PLACEHOLDER:
        upper = None
    return do_subscript(value, slice(lower, upper))


CORE_LIB_FUNCTIONS_LIST: list[Callable] = [
    print,
    sum,
    struct_literal,
    get_field,
    get_type,
    do_div,
    do_slice,
    do_subscript,
    BitwiseAnd,
    BitwiseXor,
    BitwiseNot,
    BitwiseOr,
    LogicalXor,
]

ATOMIC_EXPRESSION_FUNCTIONS = {
    **{core_func.__name__: core_func for core_func in CORE_LIB_FUNCTIONS_LIST},
}

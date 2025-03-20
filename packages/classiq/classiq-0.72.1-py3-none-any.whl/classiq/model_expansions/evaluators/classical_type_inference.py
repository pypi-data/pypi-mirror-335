from typing import Any, Union

from classiq.interface.exceptions import ClassiqExpansionError
from classiq.interface.generator.expressions.proxies.classical.classical_array_proxy import (
    ClassicalArrayProxy,
)
from classiq.interface.generator.expressions.proxies.classical.classical_struct_proxy import (
    ClassicalStructProxy,
)
from classiq.interface.generator.expressions.proxies.classical.qmod_struct_instance import (
    QmodStructInstance,
)
from classiq.interface.generator.functions.classical_type import (
    ClassicalArray,
    ClassicalList,
    ClassicalType,
)
from classiq.interface.generator.functions.type_name import TypeName
from classiq.interface.generator.types.struct_declaration import StructDeclaration


def infer_classical_type(val: Any, classical_type: ClassicalType) -> ClassicalType:
    if isinstance(classical_type, TypeName):
        return _infer_classical_struct_type(val, classical_type)
    if isinstance(classical_type, (ClassicalArray, ClassicalList)):
        return _infer_classical_array_type(val, classical_type)
    return classical_type


def _infer_classical_struct_type(val: Any, classical_type: TypeName) -> ClassicalType:
    if not isinstance(val, (QmodStructInstance, ClassicalStructProxy)):
        return classical_type
    decl = val.struct_declaration
    new_fields = {
        field_name: infer_classical_type(field_val, field_type)
        for (field_name, field_val), field_type in zip(
            val.fields.items(),
            decl.variables.values(),
            strict=True,
        )
    }
    new_classical_type = TypeName(name=decl.name)
    new_classical_type.set_classical_struct_decl(
        StructDeclaration(name=decl.name, variables=new_fields)
    )
    return new_classical_type


def _infer_classical_array_type(
    val: Any, classical_type: Union[ClassicalArray, ClassicalList]
) -> ClassicalType:
    if isinstance(val, list):
        val_length = len(val)
    elif isinstance(val, ClassicalArrayProxy):
        val_length = val.length
    else:
        raise ClassiqExpansionError(f"Array expected, got {str(val)!r}")
    if isinstance(classical_type, ClassicalArray) and val_length != classical_type.size:
        raise ClassiqExpansionError(
            f"Type mismatch: Argument has {val_length} items but "
            f"{classical_type.size} expected"
        )
    return ClassicalArray(
        element_type=(
            infer_classical_type(val[0], classical_type.element_type)
            if val_length > 0
            else classical_type.element_type
        ),
        size=val_length,
    )

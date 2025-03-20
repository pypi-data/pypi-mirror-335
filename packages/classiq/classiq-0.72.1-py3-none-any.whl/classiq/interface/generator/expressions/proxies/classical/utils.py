from classiq.interface.exceptions import ClassiqInternalExpansionError
from classiq.interface.generator.expressions.proxies.classical.classical_array_proxy import (
    ClassicalArrayProxy,
)
from classiq.interface.generator.expressions.proxies.classical.classical_proxy import (
    ClassicalProxy,
)
from classiq.interface.generator.expressions.proxies.classical.classical_scalar_proxy import (
    ClassicalScalarProxy,
)
from classiq.interface.generator.expressions.proxies.classical.classical_struct_proxy import (
    ClassicalStructProxy,
)
from classiq.interface.generator.functions.classical_type import (
    ClassicalArray,
    ClassicalType,
)
from classiq.interface.generator.functions.type_name import TypeName


def get_proxy_type(proxy: ClassicalProxy) -> ClassicalType:
    if isinstance(proxy, ClassicalScalarProxy):
        classical_type = proxy._classical_type
    elif isinstance(proxy, ClassicalArrayProxy):
        classical_type = ClassicalArray(
            element_type=proxy._element_type, size=proxy.length
        )
    elif isinstance(proxy, ClassicalStructProxy):
        classical_type = TypeName(name=proxy._decl.name)
    else:
        raise ClassiqInternalExpansionError(
            f"Unrecognized classical proxy {type(proxy).__name__}"
        )
    return classical_type

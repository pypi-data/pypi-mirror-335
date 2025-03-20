from collections.abc import Mapping
from typing import TYPE_CHECKING, Union

from sympy import Integer

from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.expressions.non_symbolic_expr import NonSymbolicExpr
from classiq.interface.generator.expressions.proxies.classical.classical_proxy import (
    ClassicalProxy,
)
from classiq.interface.model.handle_binding import (
    HandleBinding,
    SlicedHandleBinding,
    SubscriptHandleBinding,
)

if TYPE_CHECKING:
    from classiq.interface.generator.expressions.expression_types import ExpressionValue
    from classiq.interface.generator.functions.concrete_types import (
        ConcreteClassicalType,
    )


class ClassicalArrayProxy(NonSymbolicExpr, ClassicalProxy):
    def __init__(
        self, handle: HandleBinding, element_type: "ConcreteClassicalType", length: int
    ) -> None:
        super().__init__(handle)
        self._element_type = element_type
        self._length = length

    @property
    def fields(self) -> Mapping[str, "ExpressionValue"]:
        return {"len": self._length}

    @property
    def type_name(self) -> str:
        return "Array"

    @property
    def length(self) -> int:
        return self._length

    def __getitem__(self, key: Union[slice, int, Integer]) -> ClassicalProxy:
        return (
            self._get_slice(key) if isinstance(key, slice) else self._get_subscript(key)
        )

    def _get_slice(self, slice_: slice) -> ClassicalProxy:
        start = int(slice_.start)
        stop = int(slice_.stop)
        if start >= stop:
            raise ClassiqValueError("Array slice has non-positive length")
        if start < 0 or stop > self._length:
            raise ClassiqValueError("Array slice is out of bounds")
        return ClassicalArrayProxy(
            SlicedHandleBinding(
                base_handle=self.handle,
                start=Expression(expr=str(start)),
                end=Expression(expr=str(stop)),
            ),
            self._element_type,
            stop - start,
        )

    def _get_subscript(self, index_: Union[int, Integer]) -> ClassicalProxy:
        index = int(index_)
        if index < 0:
            raise ClassiqValueError(
                "Array index is out of bounds (negative indices are not supported)"
            )
        if index >= self._length:
            raise ClassiqValueError("Array index is out of bounds")
        return self._element_type.get_classical_proxy(
            SubscriptHandleBinding(
                base_handle=self._handle, index=Expression(expr=str(index_))
            )
        )

from typing import Any


class AnyClassicalValue:
    def __init__(self, expr: str) -> None:
        self._expr = expr

    def __str__(self) -> str:
        return self._expr

    def __repr__(self) -> str:
        return str(self)

    def __getitem__(self, item: Any) -> "AnyClassicalValue":
        if isinstance(item, slice):
            subscript = ""
            if item.start is not None:
                subscript += str(item.start)
            subscript += ":"
            if item.stop is not None:
                subscript += str(item.stop)
            if item.step is not None:
                subscript += f":{item.stop}"
            item = subscript
        return AnyClassicalValue(f"{self}[{item}]")

    @staticmethod
    def _binary_op(lhs: Any, rhs: Any, op: str) -> "AnyClassicalValue":
        return AnyClassicalValue(f"{lhs} {op} {rhs}")

    @staticmethod
    def _unary_op(arg: Any, op: str) -> "AnyClassicalValue":
        return AnyClassicalValue(f"{op}({arg})")

    def __add__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "+")

    def __sub__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "-")

    def __mul__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "*")

    def __truediv__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "/")

    def __floordiv__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "//")

    def __mod__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "%")

    def __pow__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "**")

    def __lshift__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "<<")

    def __rshift__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, ">>")

    def __and__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "&")

    def __xor__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "^")

    def __or__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "|")

    def __radd__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "+")

    def __rsub__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "-")

    def __rmul__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "*")

    def __rtruediv__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "/")

    def __rfloordiv__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "//")

    def __rmod__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "%")

    def __rpow__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "**")

    def __rlshift__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "<<")

    def __rrshift__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, ">>")

    def __rand__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "&")

    def __rxor__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "^")

    def __ror__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(other, self, "|")

    def __lt__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "<")

    def __le__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, "<=")

    def __eq__(self, other: Any) -> "AnyClassicalValue":  # type:ignore[override]
        return AnyClassicalValue._binary_op(self, other, "==")

    def __ne__(self, other: Any) -> "AnyClassicalValue":  # type: ignore[override]
        return AnyClassicalValue._binary_op(self, other, "!=")

    def __gt__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, ">")

    def __ge__(self, other: Any) -> "AnyClassicalValue":
        return AnyClassicalValue._binary_op(self, other, ">=")

    def __neg__(self) -> "AnyClassicalValue":
        return AnyClassicalValue._unary_op(self, "-")

    def __pos__(self) -> "AnyClassicalValue":
        return AnyClassicalValue._unary_op(self, "+")

    def __abs__(self) -> "AnyClassicalValue":
        return AnyClassicalValue._unary_op(self, "abs")

    def __invert__(self) -> "AnyClassicalValue":
        return AnyClassicalValue._unary_op(self, "~")

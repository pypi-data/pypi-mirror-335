from collections.abc import Mapping
from typing import Literal, Optional

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.model.handle_binding import ConcreteHandleBinding, HandleBinding
from classiq.interface.model.quantum_statement import QuantumOperation


class Allocate(QuantumOperation):
    kind: Literal["Allocate"]
    size: Optional[Expression] = None
    target: ConcreteHandleBinding

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        return {"out": self.target}

    @property
    def expressions(self) -> list[Expression]:
        exprs = []
        if self.size is not None:
            exprs.append(self.size)
        return exprs

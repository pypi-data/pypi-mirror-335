from typing import Optional, TypeVar
from uuid import UUID

import pydantic
from typing_extensions import Self

from classiq.interface.helpers.hashable_pydantic_base_model import (
    HashablePydanticBaseModel,
)
from classiq.interface.source_reference import SourceReference

ASTNodeType = TypeVar("ASTNodeType", bound="ASTNode")


class ASTNode(HashablePydanticBaseModel):
    source_ref: Optional[SourceReference] = pydantic.Field(default=None)
    back_ref: Optional[UUID] = pydantic.Field(default=None)

    def _as_back_ref(self: Self) -> Self:
        return self


def reset_lists(
    ast_node: ASTNodeType, statement_block_fields: list[str]
) -> ASTNodeType:
    return ast_node.model_copy(update={field: [] for field in statement_block_fields})


class HashableASTNode(ASTNode, HashablePydanticBaseModel):
    pass

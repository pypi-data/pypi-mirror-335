"""This module contains the Tag model and related enumerations."""

from typing import Literal, Optional
from uuid import UUID

from sqlmodel import SQLModel

# TagKind is the kind of tag we support.
TagKind = Literal["sample", "annotation"]


class TagBase(SQLModel):
    """Base class for the Tag model."""

    name: str
    description: Optional[str] = ""
    kind: TagKind = "sample"


class TagInput(TagBase):
    """Tag model when creating."""

    dataset_id: UUID


class TagInputBody(TagBase):
    """Tag model when creating."""


class TagUpdate(TagBase):
    """Tag model when updating."""


class TagUpdateBody(TagBase):
    """Tag model when updating."""

    dataset_id: Optional[UUID] = None  # type: ignore


class TagView(TagBase):
    """Tag model when retrieving."""

    tag_id: UUID
    kind: TagKind

"""This module defines the User model for the application."""

from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class AnnotationBase(SQLModel):
    """Base class for the Annotation model."""

    x: float
    y: float
    width: float
    height: float
    annotation_label_id: UUID = Field(
        default=None,
        index=True,
        foreign_key="annotation_labels.annotation_label_id",
    )
    dataset_id: UUID = Field(
        default=None,
        index=True,
        foreign_key="datasets.dataset_id",
    )
    sample_id: Optional[UUID] = Field(
        default=None,
        foreign_key="samples.sample_id",
    )


class AnnotationInput(AnnotationBase):
    """Annotation class when inserting."""

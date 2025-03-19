"""This module defines the AnnotationLabel model for the application."""

from sqlmodel import SQLModel


class AnnotationLabelBase(SQLModel):
    """Base class for the AnnotationLabel model."""

    annotation_label_name: str


class AnnotationLabelInput(AnnotationLabelBase):
    """AnnotationLabel class when inserting."""

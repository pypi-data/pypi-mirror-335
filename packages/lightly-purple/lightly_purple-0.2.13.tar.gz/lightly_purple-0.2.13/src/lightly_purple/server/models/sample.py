"""This module defines the User model for the application."""

from uuid import UUID

from sqlmodel import Field, SQLModel


class SampleBase(SQLModel):
    """Base class for the Sample model."""

    """The name of the image file."""
    file_name: str

    """The width of the image in pixels."""
    width: int

    """The height of the image in pixels."""
    height: int

    """The dataset ID to which the sample belongs."""
    dataset_id: UUID = Field(default=None, foreign_key="datasets.dataset_id")

    """The dataset image path."""
    file_path_abs: str


class SampleInput(SampleBase):
    """Sample class when inserting."""


class SampleViewForAnnotation(SQLModel):
    """Sample class for annotation view."""

    """The name of the image file."""
    file_path_abs: str
    sample_id: UUID

    """The width of the image in pixels."""
    width: int

    """The height of the image in pixels."""
    height: int

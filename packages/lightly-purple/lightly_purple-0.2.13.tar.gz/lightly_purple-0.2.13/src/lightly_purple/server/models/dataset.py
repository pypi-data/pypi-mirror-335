"""This module contains the Dataset model and related enumerations."""

from uuid import UUID

from sqlmodel import SQLModel


class DatasetBase(SQLModel):
    """Base class for the Dataset model."""

    name: str
    directory: str


class DatasetInput(DatasetBase):
    """Dataset class when inserting."""


class DatasetView(DatasetBase):
    """Dataset class when retrieving."""

    dataset_id: UUID

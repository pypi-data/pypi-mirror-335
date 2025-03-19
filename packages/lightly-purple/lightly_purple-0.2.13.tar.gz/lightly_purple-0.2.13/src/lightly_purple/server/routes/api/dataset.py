"""This module contains the API routes for managing datasets."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import Field, Session
from typing_extensions import Annotated

from lightly_purple.server.db import get_session
from lightly_purple.server.models import Dataset
from lightly_purple.server.models.dataset import DatasetInput, DatasetView
from lightly_purple.server.resolvers.dataset import (
    DatasetResolver,
    ExportFilter,
)
from lightly_purple.server.routes.api.status import HTTP_STATUS_NOT_FOUND
from lightly_purple.server.routes.api.validators import Paginated

dataset_router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


def get_dataset_resolver(session: SessionDep) -> DatasetResolver:
    """Create an instance of the DatasetResolver."""
    return DatasetResolver(session)


@dataset_router.post(
    "/datasets",
    response_model=DatasetView,
    status_code=201,
)
def create_dataset(
    dataset_input: DatasetInput,
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
) -> Dataset:
    """Create a new dataset in the database."""
    return handler.create(dataset_input)


@dataset_router.get("/datasets")
def read_datasets(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    paginated: Annotated[Paginated, Query()],
) -> list[DatasetView]:
    """Retrieve a list of datasets from the database."""
    return handler.get_all(**paginated.model_dump())


@dataset_router.get("/datasets/{dataset_id}")
def read_dataset(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
) -> Dataset:
    """Retrieve a single dataset from the database."""
    dataset = handler.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )
    return dataset


@dataset_router.put("/datasets/{dataset_id}")
def update_dataset(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    dataset_input: DatasetInput,
) -> Dataset:
    """Update an existing dataset in the database."""
    dataset = handler.update(dataset_id, dataset_input)
    if not dataset:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )
    return dataset


@dataset_router.delete("/datasets/{dataset_id}")
def delete_dataset(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
):
    """Delete a dataset from the database."""
    if not handler.delete(dataset_id):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )
    return {"status": "deleted"}


class ExportBody(BaseModel):
    """body parameters for including or excluding tag_ids or sample_ids."""

    include: ExportFilter | None = Field(
        None, description="include filter for sample_ids or tag_ids"
    )
    exclude: ExportFilter | None = Field(
        None, description="exclude filter for sample_ids or tag_ids"
    )


# This endpoint should be a GET, however due to the potential huge size
# of sample_ids, it is a POST request to avoid URL length limitations.
# A body with a GET request is supported by fastAPI however it has undefined
# behavior: https://fastapi.tiangolo.com/tutorial/body/
@dataset_router.post(
    "/datasets/{dataset_id}/export",
)
def export_dataset_to_absolute_paths(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    body: ExportBody,
):
    """Export dataset from the database."""
    dataset = handler.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )

    # export dataset to absolute paths
    exported = handler.export(
        dataset_id=dataset_id,
        include=body.include,
        exclude=body.exclude,
    )

    # Create a response with the exported data
    response = PlainTextResponse("\n".join(exported))

    # Add the Content-Disposition header to force download
    filename = f"{dataset.name}_exported_{datetime.now(timezone.utc)}.txt"
    response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"

    return response


"""
Endpoint to export samples from a dataset.
"""


@dataset_router.post(
    "/datasets/{dataset_id}/export/stats",
)
def export_dataset_stats(
    handler: Annotated[DatasetResolver, Depends(get_dataset_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    body: ExportBody,
) -> int:
    """Get statistics about the export query."""
    dataset = handler.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Dataset not found"
        )

    return handler.get_filtered_samples_count(
        dataset_id=dataset_id,
        include=body.include,
        exclude=body.exclude,
    )

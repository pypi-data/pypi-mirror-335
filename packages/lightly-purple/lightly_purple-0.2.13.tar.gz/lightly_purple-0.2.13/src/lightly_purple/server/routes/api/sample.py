"""This module contains the API routes for managing samples."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel, Field
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.server.db import get_session
from lightly_purple.server.models import Annotation, Sample, SampleView
from lightly_purple.server.models.sample import (
    SampleInput,
)
from lightly_purple.server.resolvers.annotation import AnnotationResolver
from lightly_purple.server.resolvers.sample import SampleResolver
from lightly_purple.server.resolvers.tag import TagResolver
from lightly_purple.server.routes.api.annotation import get_annotation_resolver
from lightly_purple.server.routes.api.dataset_tag import get_tag_resolver
from lightly_purple.server.routes.api.status import (
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
)
from lightly_purple.server.routes.api.validators import Paginated

samples_router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


def get_sample_resolver(session: SessionDep) -> SampleResolver:
    """Create an instance of the SampleResolver."""
    return SampleResolver(session)


@samples_router.post("/samples", response_model=SampleView)
def create_sample(
    handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    input_sample: SampleInput,
) -> Sample:
    """Create a new sample in the database."""
    return handler.create(input_sample)


# Define additional query parameters model
class SubqueryFilterParams(BaseModel):
    """Query parameters for filtering and doing slice and dice with samples."""

    # metadata
    min_width: int | None = Field(None, ge=0, description="Minimum width")
    max_width: int | None = Field(None, ge=0, description="Maximum width")
    min_height: int | None = Field(None, ge=0, description="Minimum height")
    max_height: int | None = Field(None, ge=0, description="Maximum height")

    # labels
    annotation_labels: list[str] | None = Field(
        None, description="Annotation labels"
    )

    # tags
    tag_ids: list[UUID] | None = Field(None, description="Tag IDs to filter by")


# TODO: this should be prefixed with /datasets/{dataset_id}/samples
class ReadSamplesQuery(SubqueryFilterParams, Paginated):
    """Query parameters for reading samples."""

    dataset_id: UUID = Field(description="Dataset ID")


@samples_router.get("/samples")
def read_samples(
    handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    query: Annotated[ReadSamplesQuery, Query()],
) -> list[SampleView]:
    """Retrieve a list of samples from the database with optional filtering."""
    return handler.get_all_by_dataset_id(
        **query.model_dump(),
    )


@samples_router.get("/samples/dimensions")
def get_sample_dimensions(
    handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    dataset_id: UUID,
    annotation_labels: Annotated[list[str] | None, Query()] = None,
) -> dict[str, int]:
    """Get min and max dimensions of samples in a dataset."""
    return handler.get_dimension_bounds(
        dataset_id, annotation_labels=annotation_labels
    )


@samples_router.get("/samples/{sample_id}")
def read_sample(
    handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    sample_id: Annotated[UUID, Path(title="Sample Id")],
) -> SampleView:
    """Retrieve a single sample from the database."""
    sample = handler.get_by_id(sample_id)
    if not sample:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Sample not found"
        )

    return sample


@samples_router.get("/samples/{sample_id}/annotations")
def read_sample_annotations(
    handler: Annotated[AnnotationResolver, Depends(get_annotation_resolver)],
    sample_id: Annotated[UUID, Path(title="Sample Id")],
) -> list[Annotation]:
    """Retrieve annotations for sample."""
    return handler.get_by_sample_id(sample_id)


@samples_router.put("/samples/{sample_id}")
def update_sample(
    handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    sample_id: Annotated[UUID, Path(title="Sample Id")],
    sample_input: Sample,
) -> Sample:
    """Update an existing sample in the database."""
    sample = handler.update(sample_id, sample_input)
    if not sample:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Sample not found"
        )
    return sample


@samples_router.delete("/samples/{sample_id}")
def delete_sample(
    handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    sample_id: Annotated[UUID, Path(title="Sample Id")],
):
    """Delete a sample from the database."""
    if not handler.delete(sample_id):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="Sample not found"
        )
    return {"status": "deleted"}


@samples_router.post(
    "/samples/{sample_id}/tag/{tag_id}",
    status_code=HTTP_STATUS_CREATED,
)
def add_tag_to_sample(
    sample_handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    sample_id: UUID,
    tag_id: UUID,
) -> bool:
    """Add sample to a tag."""
    sample = sample_handler.get_by_id(sample_id)
    if not sample:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Sample {sample_id} not found",
        )

    if not tag_handler.add_tag_to_sample(tag_id, sample):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail=f"Tag {tag_id} not found"
        )

    return True


@samples_router.delete("/samples/{sample_id}/tag/{tag_id}")
def remove_tag_from_sample(
    sample_handler: Annotated[SampleResolver, Depends(get_sample_resolver)],
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: UUID,
    sample_id: UUID,
) -> bool:
    """Remove sample from a tag."""
    sample = sample_handler.get_by_id(sample_id)
    if not sample:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Sample {sample_id} not found",
        )

    if not tag_handler.remove_tag_from_sample(tag_id, sample):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail=f"Tag {tag_id} not found"
        )

    return True

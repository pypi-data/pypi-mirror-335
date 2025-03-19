"""This module contains the API routes for managing annotations."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.server.db import get_session
from lightly_purple.server.models import (
    AnnotationViewForAnnotationLabel,
)
from lightly_purple.server.resolvers.annotation import AnnotationResolver
from lightly_purple.server.resolvers.tag import TagResolver
from lightly_purple.server.routes.api.dataset_tag import get_tag_resolver
from lightly_purple.server.routes.api.status import (
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
)
from lightly_purple.server.routes.api.validators import Paginated

annotations_router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


def get_annotation_resolver(session: SessionDep) -> AnnotationResolver:
    """Create an instance of the AnnotationResolver."""
    return AnnotationResolver(session)


@annotations_router.get("/annotations/count")
def count_annotations_by_dataset(  # noqa: PLR0913 // FIXME: refactor to use proper pydantic
    dataset_id: UUID,
    handler: Annotated[AnnotationResolver, Depends(get_annotation_resolver)],
    filtered_labels: Annotated[list[str] | None, Query()] = None,
    min_width: Annotated[int | None, Query(ge=0)] = None,
    max_width: Annotated[int | None, Query(ge=0)] = None,
    min_height: Annotated[int | None, Query(ge=0)] = None,
    max_height: Annotated[int | None, Query(ge=0)] = None,
    tag_ids: list[UUID] | None = None,
) -> list[dict[str, str | int]]:
    """Get annotation counts for a specific dataset.

    Returns a list of dictionaries with label name and count.
    """
    counts = handler.count_annotations_by_dataset(
        dataset_id,
        filtered_labels,
        min_width=min_width,
        max_width=max_width,
        min_height=min_height,
        max_height=max_height,
        tag_ids=tag_ids,
    )
    return [
        {
            "label_name": label_name,
            "current_count": current_count,
            "total_count": total_count,
        }
        for label_name, current_count, total_count in counts
    ]


@annotations_router.get("/datasets/{dataset_id}/annotations")
def read_annotations(
    dataset_id: UUID,
    handler: Annotated[AnnotationResolver, Depends(get_annotation_resolver)],
    pagination: Annotated[Paginated, Depends()],
    annotation_label_ids: Annotated[list[UUID] | None, Query()] = None,
    tag_ids: Annotated[list[UUID] | None, Query()] = None,
) -> list[AnnotationViewForAnnotationLabel]:
    """Retrieve a list of annotations from the database."""
    return handler.get_all(
        pagination={
            "offset": pagination.offset,
            "limit": pagination.limit,
        },
        filters={
            "dataset_ids": [dataset_id],
            "annotation_label_ids": annotation_label_ids or None,
            "tag_ids": tag_ids,
        },
    )


@annotations_router.post(
    "/annotations/{annotation_id}/tag/{tag_id}",
    status_code=HTTP_STATUS_CREATED,
)
def add_tag_to_annotation(
    annotation_handler: Annotated[
        AnnotationResolver, Depends(get_annotation_resolver)
    ],
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    annotation_id: UUID,
    tag_id: UUID,
) -> bool:
    """Add annotation to a tag."""
    annotation = annotation_handler.get_by_id(annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Annotation {annotation_id} not found",
        )

    if not tag_handler.add_tag_to_annotation(tag_id, annotation):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail=f"Tag {tag_id} not found"
        )

    return True


@annotations_router.delete("/annotations/{annotation_id}/tag/{tag_id}")
def remove_tag_from_annotation(
    annotation_handler: Annotated[
        AnnotationResolver, Depends(get_annotation_resolver)
    ],
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: UUID,
    annotation_id: UUID,
) -> bool:
    """Remove annotation from a tag."""
    annotation = annotation_handler.get_by_id(annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Annotation {annotation_id} not found",
        )

    if not tag_handler.remove_tag_from_annotation(tag_id, annotation):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail=f"Tag {tag_id} not found"
        )

    return True

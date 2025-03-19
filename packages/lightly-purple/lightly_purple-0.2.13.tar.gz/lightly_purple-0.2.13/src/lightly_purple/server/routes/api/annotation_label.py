"""This module contains the API routes for managing annotation labels."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing_extensions import Annotated

from lightly_purple.server.db import get_session
from lightly_purple.server.models import AnnotationLabel, AnnotationLabelView
from lightly_purple.server.models.annotation_label import AnnotationLabelInput
from lightly_purple.server.resolvers.annotation_label import (
    AnnotationLabelResolver,
)
from lightly_purple.server.routes.api.status import (
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
)

annotations_label_router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


def get_annotation_label_resolver(
    session: SessionDep,
) -> AnnotationLabelResolver:
    """Create an instance of the AnnotationLabelResolver."""
    return AnnotationLabelResolver(session)


@annotations_label_router.post(
    "/annotation_labels",
    response_model=AnnotationLabelView,
    status_code=HTTP_STATUS_CREATED,
)
def create_annotation_label(
    input_label: AnnotationLabelInput,
    handler: Annotated[
        AnnotationLabelResolver, Depends(get_annotation_label_resolver)
    ],
) -> AnnotationLabel:
    """Create a new annotation label in the database."""
    return handler.create(input_label)


@annotations_label_router.get("/annotation_labels")
def read_annotation_labels(
    handler: Annotated[
        AnnotationLabelResolver, Depends(get_annotation_label_resolver)
    ],
) -> list[AnnotationLabel]:
    """Retrieve a list of annotation labels from the database."""
    return handler.get_all()


@annotations_label_router.get("/annotation_labels/{label_id}")
def read_annotation_label(
    label_id: UUID,
    handler: Annotated[
        AnnotationLabelResolver, Depends(get_annotation_label_resolver)
    ],
) -> AnnotationLabel:
    """Retrieve a single annotation label from the database."""
    label = handler.get_by_id(label_id)
    if not label:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail="Annotation label not found",
        )
    return label


@annotations_label_router.put("/annotation_labels/{label_id}")
def update_annotation_label(
    label_id: UUID,
    label_input: AnnotationLabel,
    handler: Annotated[
        AnnotationLabelResolver, Depends(get_annotation_label_resolver)
    ],
) -> AnnotationLabel:
    """Update an existing annotation label in the database."""
    label = handler.update(label_id, label_input)
    if not label:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail="Annotation label not found",
        )
    return label


@annotations_label_router.delete("/annotation_labels/{label_id}")
def delete_annotation_label(
    label_id: UUID,
    handler: Annotated[
        AnnotationLabelResolver, Depends(get_annotation_label_resolver)
    ],
):
    """Delete an annotation label from the database."""
    if not handler.delete(label_id):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail="Annotation label not found",
        )
    return {"status": "deleted"}

"""This module contains the API routes for managing tags."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Field, Session
from typing_extensions import Annotated

from lightly_purple.server.db import get_session
from lightly_purple.server.models import Tag
from lightly_purple.server.models.tag import (
    TagInput,
    TagInputBody,
    TagUpdate,
    TagUpdateBody,
    TagView,
)
from lightly_purple.server.resolvers.tag import TagResolver
from lightly_purple.server.routes.api.status import (
    HTTP_STATUS_CONFLICT,
    HTTP_STATUS_CREATED,
    HTTP_STATUS_NOT_FOUND,
)
from lightly_purple.server.routes.api.validators import Paginated

tag_router = APIRouter()
SessionDep = Annotated[Session, Depends(get_session)]


def get_tag_resolver(session: SessionDep) -> TagResolver:
    """Create an instance of the TagResolver."""
    return TagResolver(session)


@tag_router.post(
    "/datasets/{dataset_id}/tags",
    response_model=TagView,
    status_code=HTTP_STATUS_CREATED,
)
def create_tag(
    handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    body: TagInputBody,
) -> Tag:
    """Create a new tag in the database."""
    try:
        return handler.create(
            TagInput(
                **body.model_dump(exclude_unset=True), dataset_id=dataset_id
            )
        )
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTP_STATUS_CONFLICT,
            detail=f"""
                Tag with name {body.name} already exists
                in the dataset {dataset_id}.
            """,
        ) from e


@tag_router.get("/datasets/{dataset_id}/tags")
def read_tags(
    handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    paginated: Annotated[Paginated, Query()],
) -> list[TagView]:
    """Retrieve a list of tags from the database."""
    return handler.get_all_by_dataset_id(
        **paginated.model_dump(),
        dataset_id=dataset_id,
    )


@tag_router.get("/datasets/{dataset_id}/tags/{tag_id}")
def read_tag(
    handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    tag_id: Annotated[UUID, Path(title="Tag Id")],
) -> Tag:
    """Retrieve a single tag from the database."""
    tag = handler.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"""
            Tag with id {tag_id} for dataset {dataset_id} not found.
            """,
        )
    return tag


@tag_router.put("/datasets/{dataset_id}/tags/{tag_id}")
def update_tag(
    handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    dataset_id: Annotated[UUID, Path(title="Dataset Id")],
    tag_id: Annotated[UUID, Path(title="Tag Id")],
    body: TagUpdateBody,
) -> Tag:
    """Update an existing tag in the database."""
    try:
        tag = handler.update(
            tag_id,
            TagUpdate(
                **body.model_dump(exclude_unset=True), dataset_id=dataset_id
            ),
        )
        if not tag:
            raise HTTPException(
                status_code=HTTP_STATUS_NOT_FOUND,
                detail=f"Tag with id {tag_id} not found.",
            )
    except IntegrityError as e:
        raise HTTPException(
            status_code=HTTP_STATUS_CONFLICT,
            detail=f"""
                Cannot update tag. Tag with name {body.name}
                already exists in the dataset {dataset_id}.
            """,
        ) from e
    return tag


@tag_router.delete("/datasets/{dataset_id}/tags/{tag_id}")
def delete_tag(
    handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: Annotated[UUID, Path(title="Tag Id")],
):
    """Delete a tag from the database."""
    if not handler.delete(tag_id):
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND, detail="tag not found"
        )
    return {"status": "deleted"}


class SampleIdsBody(BaseModel):
    """body parameters for adding or removing thing_ids."""

    sample_ids: list[UUID] | None = Field(
        None, description="sample ids to add/remove"
    )


@tag_router.post(
    "/datasets/{dataset_id}/tags/{tag_id}/add/samples",
    status_code=HTTP_STATUS_CREATED,
)
def add_sample_ids_to_tag_id(
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: UUID,
    body: SampleIdsBody,
) -> bool:
    """Add sample_ids to a tag_id."""
    tag = tag_handler.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't add sample_ids.",
        )

    tag_handler.add_sample_ids_to_tag_id(tag_id, **body.model_dump())
    return True


@tag_router.delete(
    "/datasets/{dataset_id}/tags/{tag_id}/remove/samples",
)
def remove_thing_ids_to_tag_id(
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: UUID,
    body: SampleIdsBody,
) -> bool:
    """Add thing_ids to a tag_id."""
    tag = tag_handler.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't remove samples.",
        )

    tag_handler.remove_sample_ids_from_tag_id(tag_id, **body.model_dump())
    return True


class AnnotationIdsBody(BaseModel):
    """body parameters for adding or removing annotation_ids."""

    annotation_ids: list[UUID] | None = Field(
        None, description="annotation ids to add/remove"
    )


@tag_router.post(
    "/datasets/{dataset_id}/tags/{tag_id}/add/annotations",
    status_code=HTTP_STATUS_CREATED,
)
def add_annotation_ids_to_tag_id(
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: UUID,
    body: AnnotationIdsBody,
) -> bool:
    """Add thing_ids to a tag_id."""
    tag = tag_handler.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't add annotations.",
        )

    tag_handler.add_annotation_ids_to_tag_id(tag_id, **body.model_dump())
    return True


@tag_router.delete(
    "/datasets/{dataset_id}/tags/{tag_id}/remove/annotations",
)
def remove_annotation_ids_to_tag_id(
    tag_handler: Annotated[TagResolver, Depends(get_tag_resolver)],
    tag_id: UUID,
    body: AnnotationIdsBody,
) -> bool:
    """Add thing_ids to a tag_id."""
    tag = tag_handler.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=HTTP_STATUS_NOT_FOUND,
            detail=f"Tag {tag_id} not found, can't remove annotations.",
        )

    tag_handler.remove_annotation_ids_from_tag_id(tag_id, **body.model_dump())
    return True

"""Handler for database operations related to tags."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, delete, select

from lightly_purple.server.models import (
    Annotation,
    AnnotationTagLink,
    Sample,
    SampleTagLink,
    Tag,
)
from lightly_purple.server.models.tag import TagInput, TagUpdate, TagView


class TagResolver:
    """Resolver for the tag model."""

    def __init__(self, session: Session):  # noqa: D107
        self.session = session

    def create(self, tag: TagInput) -> Tag:
        """Create a new tag in the database."""
        db_tag = Tag.model_validate(tag)
        self.session.add(db_tag)
        self.session.commit()
        self.session.refresh(db_tag)
        return db_tag

    def get_all_by_dataset_id(
        self, dataset_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[TagView]:
        """Retrieve all tags with pagination."""
        tags = self.session.exec(
            select(Tag)
            .where(Tag.dataset_id == dataset_id)
            .offset(offset)
            .limit(limit)
        ).all()
        return list(tags) if tags else []

    def get_by_id(self, tag_id: UUID) -> Tag | None:
        """Retrieve a single tag by ID."""
        return self.session.exec(
            select(Tag).where(Tag.tag_id == tag_id)
        ).one_or_none()

    def get_by_name(self, tag_name: str) -> Tag | None:
        """Retrieve a single tag by ID."""
        return self.session.exec(
            select(Tag).where(Tag.name == tag_name)
        ).one_or_none()

    def update(self, tag_id: UUID, tag_data: TagUpdate) -> Tag | None:
        """Update an existing tag."""
        tag = self.get_by_id(tag_id)
        if not tag:
            return None

        # due to duckdb/OLAP optimisations, update operations effecting unique
        # constraints (e.g colums) will lead to a unique constraint violation.
        # This is due to a update is implemented as delete+insert. The error
        # happens only within the same session.
        # To fix it, we can delete, commit + insert a new tag.
        # https://duckdb.org/docs/sql/indexes#over-eager-unique-constraint-checking
        self.session.delete(tag)
        self.session.commit()

        # create clone of tag with updated values
        tag_updated = Tag.model_validate(tag)
        tag_updated.name = tag_data.name
        tag_updated.description = tag_data.description
        tag_updated.updated_at = datetime.now(timezone.utc)

        self.session.add(tag_updated)
        self.session.commit()
        self.session.refresh(tag_updated)
        return tag_updated

    def delete(self, tag_id: UUID) -> bool:
        """Delete a tag."""
        tag = self.get_by_id(tag_id)
        if not tag:
            return False

        self.session.delete(tag)
        self.session.commit()
        return True

    def add_tag_to_sample(
        self,
        tag_id: UUID,
        sample: Sample,
    ) -> Sample | None:
        """Add a tag to a sample."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "sample":
            raise ValueError(f"Tag {tag_id} is not of kind 'sample'")

        sample.tags.append(tag)
        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        return sample

    def remove_tag_from_sample(
        self,
        tag_id: UUID,
        sample: Sample,
    ) -> Sample | None:
        """Remove a tag from a sample."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "sample":
            raise ValueError(f"Tag {tag_id} is not of kind 'sample'")

        sample.tags.remove(tag)
        self.session.add(sample)
        self.session.commit()
        self.session.refresh(sample)
        return sample

    def add_tag_to_annotation(
        self,
        tag_id: UUID,
        annotation: Annotation,
    ) -> Annotation | None:
        """Add a tag to a annotation."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "annotation":
            raise ValueError(f"Tag {tag_id} is not of kind 'annotation'")

        annotation.tags.append(tag)
        self.session.add(annotation)
        self.session.commit()
        self.session.refresh(annotation)
        return annotation

    def remove_tag_from_annotation(
        self,
        tag_id: UUID,
        annotation: Annotation,
    ) -> Annotation | None:
        """Remove a tag from a annotation."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "annotation":
            raise ValueError(f"Tag {tag_id} is not of kind 'annotation'")

        annotation.tags.remove(tag)
        self.session.add(annotation)
        self.session.commit()
        self.session.refresh(annotation)
        return annotation

    def add_sample_ids_to_tag_id(
        self,
        tag_id: UUID,
        sample_ids: list[UUID],
    ) -> Tag | None:
        """Add a list of sample_ids to a tag."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "sample":
            raise ValueError(f"Tag {tag_id} is not of kind 'sample'")

        for sample_id in sample_ids:
            self.session.merge(
                SampleTagLink(sample_id=sample_id, tag_id=tag_id)
            )

        self.session.commit()
        self.session.refresh(tag)
        return tag

    def remove_sample_ids_from_tag_id(
        self,
        tag_id: UUID,
        sample_ids: list[UUID],
    ) -> Tag | None:
        """Remove a list of sample_ids to a tag."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "sample":
            raise ValueError(f"Tag {tag_id} is not of kind 'sample'")

        self.session.exec(
            delete(SampleTagLink).where(
                SampleTagLink.tag_id == tag_id,
                SampleTagLink.sample_id.in_(sample_ids),
            )
        )

        self.session.commit()
        self.session.refresh(tag)
        return tag

    def add_annotation_ids_to_tag_id(
        self,
        tag_id: UUID,
        annotation_ids: list[UUID],
    ) -> Tag | None:
        """Add a list of annotation_ids to a tag."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "annotation":
            raise ValueError(f"Tag {tag_id} is not of kind 'annotation'")

        for annotation_id in annotation_ids:
            self.session.merge(
                AnnotationTagLink(
                    tag_id=tag_id,
                    annotation_id=annotation_id,
                )
            )

        self.session.commit()
        self.session.refresh(tag)
        return tag

    def remove_annotation_ids_from_tag_id(
        self,
        tag_id: UUID,
        annotation_ids: list[UUID],
    ) -> Tag | None:
        """Remove a list of things to a tag."""
        tag = self.get_by_id(tag_id)
        if not tag or not tag.tag_id:
            return None
        if tag.kind != "annotation":
            raise ValueError(f"Tag {tag_id} is not of kind 'annotation'")

        self.session.exec(
            delete(AnnotationTagLink).where(
                AnnotationTagLink.tag_id == tag_id,
                AnnotationTagLink.annotation_id.in_(annotation_ids),
            )
        )

        self.session.commit()
        self.session.refresh(tag)
        return tag

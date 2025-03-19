"""Handler for database operations related to annotations."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field
from sqlmodel import Session, func, select

from lightly_purple.server.models import (
    Annotation,
    AnnotationLabel,
    Sample,
    Tag,
)
from lightly_purple.server.models.annotation import AnnotationInput
from lightly_purple.server.routes.api.validators import Paginated


class AnnotationsFilterParams(BaseModel):
    """Encapsulates filter parameters for querying annotations."""

    dataset_ids: list[UUID] | None = Field(
        default=None, description="List of dataset UUIDs"
    )
    annotation_label_ids: list[UUID] | None = Field(
        default=None, description="List of annotation label UUIDs"
    )
    tag_ids: list[UUID] | None = Field(
        default=None, description="List of tag UUIDs"
    )


class AnnotationResolver:
    """Resolver for the Annotation model."""

    def __init__(self, session: Session):  # noqa: D107
        self.session = session

    def create(self, annotation: AnnotationInput) -> Annotation:
        """Create a new annotation in the database."""
        db_annotation = Annotation.model_validate(annotation)
        self.session.add(db_annotation)
        self.session.commit()
        self.session.refresh(db_annotation)
        return db_annotation

    def create_many(self, annotations: list[AnnotationInput]) -> None:
        """Create many annotations in a single commit. No return values."""
        db_annotations = [Annotation.model_validate(a) for a in annotations]
        self.session.bulk_save_objects(db_annotations)
        self.session.commit()

    def get_all(
        self,
        pagination: dict | Paginated | None = None,
        filters: AnnotationsFilterParams | None = None,
    ) -> list[Annotation]:
        """Retrieve all annotations from the database."""
        if pagination is None:
            pagination = Paginated()
        elif isinstance(pagination, dict):
            pagination = Paginated(**pagination)

        if filters is None:
            filters = AnnotationsFilterParams()
        elif isinstance(filters, dict):
            filters = AnnotationsFilterParams(**filters)

        query = select(Annotation)

        # Apply filters if provided
        if filters:
            if filters.annotation_label_ids:
                query = query.where(
                    Annotation.annotation_label_id.in_(
                        filters.annotation_label_ids
                    )
                )

            if filters.dataset_ids:
                query = query.where(
                    Annotation.dataset_id.in_(filters.dataset_ids)
                )

            # filter by tag_ids
            if filters.tag_ids:
                query = (
                    query.join(Annotation.tags)
                    .where(Annotation.tags.any(Tag.tag_id.in_(filters.tag_ids)))
                    .distinct()
                )

        annotations = self.session.exec(
            query.offset(pagination.offset).limit(pagination.limit)
        ).all()
        return annotations or []

    def get_by_id(self, annotation_id: UUID) -> Annotation | None:
        """Retrieve a single annotation by ID."""
        return self.session.exec(
            select(Annotation).where(Annotation.annotation_id == annotation_id)
        ).one_or_none()

    def update(
        self, annotation_id: UUID, annotation_data: AnnotationInput
    ) -> Annotation | None:
        """Update an existing annotation."""
        annotation = self.get_by_id(annotation_id)
        if not annotation:
            return None

        annotation.x = annotation_data.x
        annotation.y = annotation_data.y
        annotation.width = annotation_data.width
        annotation.height = annotation_data.height

        self.session.commit()
        self.session.refresh(annotation)
        return annotation

    def delete(self, annotation_id: UUID) -> bool:
        """Delete an annotation."""
        annotation = self.get_by_id(annotation_id)
        if not annotation:
            return False

        self.session.delete(annotation)
        self.session.commit()
        return True

    def count_annotations_by_dataset(  # noqa: PLR0913 // FIXME: refactor to use proper pydantic
        self,
        dataset_id: UUID,
        filtered_labels: list[str] | None = None,
        min_width: int | None = None,
        max_width: int | None = None,
        min_height: int | None = None,
        max_height: int | None = None,
        tag_ids: list[UUID] | None = None,
    ) -> list[tuple[str, int, int]]:
        """Count annotations for a specific dataset.

        Annotations for a specific dataset are grouped by annotation
        label name and counted for total and filtered.
        """
        # Query for total counts (unfiltered)
        total_counts_query = (
            select(
                AnnotationLabel.annotation_label_name,
                func.count(Annotation.annotation_id).label("total_count"),
            )
            .join(
                Annotation,
                Annotation.annotation_label_id
                == AnnotationLabel.annotation_label_id,
            )
            .join(Sample, Sample.sample_id == Annotation.sample_id)
            .where(Sample.dataset_id == dataset_id)
            .group_by(AnnotationLabel.annotation_label_name)
            .order_by(AnnotationLabel.annotation_label_name.asc())
        )

        total_counts = {
            row[0]: row[1]
            for row in self.session.exec(total_counts_query).all()
        }

        # Build filtered query for current counts
        filtered_query = (
            select(
                AnnotationLabel.annotation_label_name,
                func.count(Annotation.annotation_id).label("current_count"),
            )
            .join(
                Annotation,
                Annotation.annotation_label_id
                == AnnotationLabel.annotation_label_id,
            )
            .join(Sample, Sample.sample_id == Annotation.sample_id)
            .where(Sample.dataset_id == dataset_id)
        )

        # Add dimension filters
        if min_width is not None:
            filtered_query = filtered_query.where(Sample.width >= min_width)
        if max_width is not None:
            filtered_query = filtered_query.where(Sample.width <= max_width)
        if min_height is not None:
            filtered_query = filtered_query.where(Sample.height >= min_height)
        if max_height is not None:
            filtered_query = filtered_query.where(Sample.height <= max_height)

        # Add label filter if specified
        if filtered_labels:
            filtered_query = filtered_query.where(
                Sample.sample_id.in_(
                    select(Sample.sample_id)
                    .join(Annotation, Sample.sample_id == Annotation.sample_id)
                    .join(
                        AnnotationLabel,
                        Annotation.annotation_label_id
                        == AnnotationLabel.annotation_label_id,
                    )
                    .where(
                        AnnotationLabel.annotation_label_name.in_(
                            filtered_labels
                        )
                    )
                )
            )

        # filter by tag_ids
        if tag_ids:
            filtered_query = (
                filtered_query.join(Annotation.tags)
                .where(Annotation.tags.any(Tag.tag_id.in_(tag_ids)))
                .distinct()
            )

        # Group by label name and sort
        filtered_query = filtered_query.group_by(
            AnnotationLabel.annotation_label_name
        ).order_by(AnnotationLabel.annotation_label_name.asc())

        _rows = self.session.exec(filtered_query).all()

        current_counts = {row[0]: row[1] for row in _rows}

        return [
            (label, current_counts.get(label, 0), total_count)
            for label, total_count in total_counts.items()
        ]

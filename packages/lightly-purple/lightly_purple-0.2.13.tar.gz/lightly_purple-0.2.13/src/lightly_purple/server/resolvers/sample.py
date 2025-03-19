"""Handler for database operations related to samples."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlmodel import Session, func, select

from lightly_purple.server.models import (
    Annotation,
    AnnotationLabel,
    Sample,
    Tag,
)
from lightly_purple.server.models.sample import SampleInput


class SampleResolver:
    """Resolver for the Sample model."""

    def __init__(self, session: Session):  # noqa: D107
        self.session = session

    def create(self, sample: SampleInput) -> Sample:
        """Create a new sample in the database."""
        db_sample = Sample.model_validate(sample)
        self.session.add(db_sample)
        self.session.commit()
        self.session.refresh(db_sample)
        return db_sample

    def get_by_id(self, sample_id: UUID) -> Sample | None:
        """Retrieve a single sample by ID."""
        return self.session.exec(
            select(Sample).where(Sample.sample_id == sample_id)
        ).one_or_none()

    def get_all_by_dataset_id(  # noqa: PLR0913 // FIXME: refactor to use proper pydantic
        self,
        dataset_id: UUID,
        offset: int = 0,
        limit: int = 10,
        min_width: int | None = None,
        max_width: int | None = None,
        min_height: int | None = None,
        max_height: int | None = None,
        annotation_labels: list[str] | None = None,
        tag_ids: list[UUID] | None = None,
    ) -> list[Sample]:
        """Retrieve samples for a specific dataset with optional filtering."""
        query = select(Sample).where(Sample.dataset_id == dataset_id)
        # Add dimension filters
        if min_width is not None:
            query = query.where(Sample.width >= min_width)
        if max_width is not None:
            query = query.where(Sample.width <= max_width)
        if min_height is not None:
            query = query.where(Sample.height >= min_height)
        if max_height is not None:
            query = query.where(Sample.height <= max_height)

        if annotation_labels:
            query = (
                query.join(Annotation, Sample.sample_id == Annotation.sample_id)
                .join(
                    AnnotationLabel,
                    Annotation.annotation_label_id
                    == AnnotationLabel.annotation_label_id,
                )
                .where(
                    AnnotationLabel.annotation_label_name.in_(annotation_labels)
                )
                .distinct()
            )

        if tag_ids:
            query = (
                query.join(Sample.tags)
                .where(Sample.tags.any(Tag.tag_id.in_(tag_ids)))
                .distinct()
            )

        query = (
            query.order_by(Sample.created_at.asc()).offset(offset).limit(limit)
        )
        return self.session.exec(query).all()

    def get_dimension_bounds(
        self,
        dataset_id: UUID,
        annotation_labels: list[str] | None = None,
        tag_ids: list[UUID] | None = None,
    ) -> dict[str, int]:
        """Get min and max dimensions of samples in a dataset."""
        # Prepare the base query for dimensions
        query = select(
            func.min(Sample.width).label("min_width"),
            func.max(Sample.width).label("max_width"),
            func.min(Sample.height).label("min_height"),
            func.max(Sample.height).label("max_height"),
        )

        if annotation_labels:
            # Subquery to filter samples matching all annotation labels
            label_filter = (
                select(Sample.sample_id)
                .join(Annotation, Sample.sample_id == Annotation.sample_id)
                .join(
                    AnnotationLabel,
                    Annotation.annotation_label_id
                    == AnnotationLabel.annotation_label_id,
                )
                .where(
                    Sample.dataset_id == dataset_id,
                    AnnotationLabel.annotation_label_name.in_(
                        annotation_labels
                    ),
                )
                .group_by(Sample.sample_id)
                .having(
                    func.count(AnnotationLabel.annotation_label_name.distinct())
                    == len(annotation_labels)
                )
            )
            # Filter the dimension query based on the subquery
            query = query.where(Sample.sample_id.in_(label_filter))
        else:
            # If no labels specified, filter dimensions
            # for all samples in the dataset
            query = query.where(Sample.dataset_id == dataset_id)

        if tag_ids:
            query = (
                query.join(Sample.tags)
                .where(Sample.tags.any(Tag.tag_id.in_(tag_ids)))
                .distinct()
            )

        result = self.session.exec(query).one()
        return {
            key: value
            for key, value in result._asdict().items()
            if value is not None
        }

    def update(
        self, sample_id: UUID, sample_data: SampleInput
    ) -> Sample | None:
        """Update an existing sample."""
        sample = self.get_by_id(sample_id)
        if not sample:
            return None

        sample.file_name = sample_data.file_name
        sample.width = sample_data.width
        sample.height = sample_data.height
        sample.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(sample)
        return sample

    def delete(self, sample_id: UUID) -> bool:
        """Delete a sample."""
        sample = self.get_by_id(sample_id)
        if not sample:
            return False

        self.session.delete(sample)
        self.session.commit()
        return True

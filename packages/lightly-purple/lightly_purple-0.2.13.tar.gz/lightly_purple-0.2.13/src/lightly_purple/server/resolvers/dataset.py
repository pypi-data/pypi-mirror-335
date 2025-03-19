"""Handler for database operations related to datasets."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field, model_validator
from sqlmodel import Session, and_, func, or_, select

from lightly_purple.server.models import Annotation, Dataset, Sample, Tag
from lightly_purple.server.models.dataset import DatasetInput


class ExportFilter(BaseModel):
    """Export Filter to be used for including or excluding."""

    tag_ids: list[UUID] | None = Field(
        default=None, min_length=1, description="List of tag UUIDs"
    )
    sample_ids: list[UUID] | None = Field(
        default=None, min_length=1, description="List of sample UUIDs"
    )
    annotation_ids: list[UUID] | None = Field(
        default=None, min_length=1, description="List of annotation UUIDs"
    )

    @model_validator(mode="after")
    def check_exactly_one(cls, model: ExportFilter) -> ExportFilter:
        """Ensure that exactly one of the fields is set."""
        count = (
            (model.tag_ids is not None)
            + (model.sample_ids is not None)
            + (model.annotation_ids is not None)
        )
        if count != 1:
            raise ValueError(
                "Either tag_ids, sample_ids, or annotation_ids must be set."
            )
        return model


class DatasetResolver:
    """Resolver for the Dataset model."""

    def __init__(self, session: Session):  # noqa: D107
        self.session = session

    def create(self, dataset: DatasetInput) -> Dataset:
        """Create a new dataset in the database."""
        db_dataset = Dataset.model_validate(dataset)
        self.session.add(db_dataset)
        self.session.commit()
        self.session.refresh(db_dataset)
        return db_dataset

    def get_all(self, offset: int = 0, limit: int = 100) -> list[Dataset]:
        """Retrieve all datasets with pagination."""
        datasets = self.session.exec(
            select(Dataset).offset(offset).limit(limit)
        ).all()
        return list(datasets) if datasets else []

    def get_by_id(self, dataset_id: UUID) -> Dataset | None:
        """Retrieve a single dataset by ID."""
        return self.session.exec(
            select(Dataset).where(Dataset.dataset_id == dataset_id)
        ).one_or_none()

    def update(
        self, dataset_id: UUID, dataset_data: DatasetInput
    ) -> Dataset | None:
        """Update an existing dataset."""
        dataset = self.get_by_id(dataset_id)
        if not dataset:
            return None

        dataset.name = dataset_data.name
        dataset.directory = dataset_data.directory
        dataset.updated_at = datetime.now(timezone.utc)

        self.session.commit()
        self.session.refresh(dataset)
        return dataset

    def delete(self, dataset_id: UUID) -> bool:
        """Delete a dataset."""
        dataset = self.get_by_id(dataset_id)
        if not dataset:
            return False

        self.session.delete(dataset)
        self.session.commit()
        return True

    def _build_export_query(  # noqa: C901
        self,
        dataset_id: UUID,
        include: ExportFilter | None = None,
        exclude: ExportFilter | None = None,
    ) -> select:
        """Build the export query based on filters.

        Args:
            dataset_id: UUID of the dataset.
            include: Filter to include samples.
            exclude: Filter to exclude samples.

        Returns:
            SQLModel select query
        """
        if not include and not exclude:
            raise ValueError("Include or exclude filter is required.")
        if include and exclude:
            raise ValueError("Cannot include and exclude at the same time.")

        # include tags or sample_ids or annotation_ids from result
        if include:
            if include.tag_ids:
                return (
                    select(Sample)
                    .where(Sample.dataset_id == dataset_id)
                    .where(
                        or_(
                            # Samples with matching sample tags
                            Sample.tags.any(
                                and_(
                                    Tag.kind == "sample",
                                    Tag.tag_id.in_(include.tag_ids),
                                )
                            ),
                            # Samples with matching annotation tags
                            Sample.annotations.any(
                                Annotation.tags.any(
                                    and_(
                                        Tag.kind == "annotation",
                                        Tag.tag_id.in_(include.tag_ids),
                                    )
                                )
                            ),
                        )
                    )
                    .order_by(Sample.sample_id)
                    .distinct()
                )

            # get samples by specific sample_ids
            if include.sample_ids:
                return (
                    select(Sample)
                    .where(Sample.dataset_id == dataset_id)
                    .where(Sample.sample_id.in_(include.sample_ids))
                    .order_by(Sample.sample_id)
                    .distinct()
                )

            # get samples by specific annotation_ids
            if include.annotation_ids:
                return (
                    select(Sample)
                    .join(Sample.annotations)
                    .where(Annotation.dataset_id == dataset_id)
                    .where(Annotation.annotation_id.in_(include.annotation_ids))
                    .order_by(Sample.sample_id)
                    .distinct()
                )

        # exclude tags or sample_ids or annotation_ids from result
        elif exclude:
            if exclude.tag_ids:
                return (
                    select(Sample)
                    .where(Sample.dataset_id == dataset_id)
                    .where(
                        and_(
                            ~Sample.tags.any(
                                and_(
                                    Tag.kind == "sample",
                                    Tag.tag_id.in_(exclude.tag_ids),
                                )
                            ),
                            or_(
                                ~Sample.annotations.any(),
                                ~Sample.annotations.any(
                                    Annotation.tags.any(
                                        and_(
                                            Tag.kind == "annotation",
                                            Tag.tag_id.in_(exclude.tag_ids),
                                        )
                                    )
                                ),
                            ),
                        )
                    )
                    .order_by(Sample.sample_id)
                    .distinct()
                )
            if exclude.sample_ids:
                return (
                    select(Sample)
                    .where(Sample.dataset_id == dataset_id)
                    .where(Sample.sample_id.notin_(exclude.sample_ids))
                    .order_by(Sample.sample_id)
                    .distinct()
                )
            if exclude.annotation_ids:
                return (
                    select(Sample)
                    .where(Sample.dataset_id == dataset_id)
                    .where(
                        or_(
                            ~Sample.annotations.any(),
                            ~Sample.annotations.any(
                                Annotation.annotation_id.in_(
                                    exclude.annotation_ids
                                )
                            ),
                        )
                    )
                    .order_by(Sample.sample_id)
                    .distinct()
                )

        raise ValueError("Invalid include or export filter combination.")

    # TODO: this fn should be moved to a "business logic" layer outside of the
    # resolvers and abstracted in to reusable components.
    # https://linear.app/lightly/issue/LIG-6196/figure-out-architecture-follow-up-changes-in-python-package
    # TODO: this should be abstracted to allow different export formats.
    def export(
        self,
        dataset_id: UUID,
        include: ExportFilter | None = None,
        exclude: ExportFilter | None = None,
    ) -> list[str]:
        """Retrieve samples for exporting from a dataset.

        Only one of include or exclude should be set and not both.
        Furthermore, the include and exclude filter can only have
        one type (tag_ids, sample_ids or annotations_ids) set.

        Args:
            dataset_id: UUID of the dataset.
            include: Filter to include samples.
            exclude: Filter to exclude samples.

        Returns:
            List of file paths
        """
        query = self._build_export_query(dataset_id, include, exclude)
        result = self.session.exec(query).all()
        return [sample.file_path_abs for sample in result]

    def get_filtered_samples_count(
        self,
        dataset_id: UUID,
        include: ExportFilter | None = None,
        exclude: ExportFilter | None = None,
    ) -> int:
        """Get statistics about the export query.

        Only one of include or exclude should be set and not both.
        Furthermore, the include and exclude filter can only have
        one type (tag_ids, sample_ids or annotations_ids) set.

        Args:
            dataset_id: UUID of the dataset.
            include: Filter to include samples.
            exclude: Filter to exclude samples.

        Returns:
            Count of files to be exported
        """
        query = self._build_export_query(dataset_id, include, exclude)
        count_query = select(func.count()).select_from(query.subquery())
        return self.session.exec(count_query).one() or 0

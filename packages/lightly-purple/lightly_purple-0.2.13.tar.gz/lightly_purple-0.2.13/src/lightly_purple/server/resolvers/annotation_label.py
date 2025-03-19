"""Handler for database operations related to annotation labels."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import Session, select

from lightly_purple.server.models import AnnotationLabel
from lightly_purple.server.models.annotation_label import (
    AnnotationLabelInput,
)


class AnnotationLabelResolver:
    """Resolver for the AnnotationLabel model."""

    def __init__(self, session: Session):  # noqa: D107
        self.session = session

    def create(self, label: AnnotationLabelInput) -> AnnotationLabel:
        """Create a new annotation label in the database."""
        db_label = AnnotationLabel.model_validate(label)
        self.session.add(db_label)
        self.session.commit()
        self.session.refresh(db_label)
        return db_label

    def get_all(self) -> list[AnnotationLabel]:
        """Retrieve all annotation labels."""
        labels = self.session.exec(select(AnnotationLabel)).all()
        return list(labels) if labels else []

    def get_by_id(self, label_id: UUID) -> AnnotationLabel | None:
        """Retrieve a single annotation label by ID."""
        return self.session.exec(
            select(AnnotationLabel).where(
                AnnotationLabel.annotation_label_id == label_id
            )
        ).one_or_none()

    def update(
        self, label_id: UUID, label_data: AnnotationLabelInput
    ) -> AnnotationLabel | None:
        """Update an existing annotation label."""
        label = self.get_by_id(label_id)
        if not label:
            return None

        label.annotation_label_name = label_data.annotation_label_name
        self.session.commit()
        self.session.refresh(label)
        return label

    def delete(self, label_id: UUID) -> bool:
        """Delete an annotation label."""
        label = self.get_by_id(label_id)
        if not label:
            return False

        self.session.delete(label)
        self.session.commit()
        return True

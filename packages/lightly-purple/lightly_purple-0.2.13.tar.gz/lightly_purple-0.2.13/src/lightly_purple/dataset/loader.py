"""Dataset functionality module."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from uuid import UUID

from labelformat.model.bounding_box import BoundingBoxFormat
from labelformat.model.object_detection import ObjectDetectionInput
from tqdm import tqdm

from lightly_purple.dataset.env import APP_URL, PURPLE_HOST, PURPLE_PORT
from lightly_purple.server.db import db_manager
from lightly_purple.server.models import Dataset
from lightly_purple.server.models.annotation import AnnotationInput
from lightly_purple.server.models.annotation_label import AnnotationLabelInput
from lightly_purple.server.models.dataset import DatasetInput
from lightly_purple.server.models.sample import SampleInput
from lightly_purple.server.models.tag import TagInput
from lightly_purple.server.resolvers.annotation import AnnotationResolver
from lightly_purple.server.resolvers.annotation_label import (
    AnnotationLabelResolver,
)
from lightly_purple.server.resolvers.dataset import DatasetResolver
from lightly_purple.server.resolvers.sample import SampleResolver
from lightly_purple.server.resolvers.tag import TagResolver
from lightly_purple.server.server import Server

from .coco_loader import COCODatasetLoader
from .yolo_loader import YOLODatasetLoader

# Constants
ANNOTATION_BATCH_SIZE = 64  # Number of annotations to process in a single batch


class DatasetLoader:
    """Class responsible for loading datasets from various sources."""

    def __init__(self) -> None:
        """Initialize the dataset loader."""
        self._yolo_loader: YOLODatasetLoader | None = None
        self._coco_loader: COCODatasetLoader | None = None
        self._dataset: Dataset | None = None
        with db_manager.session() as session:
            self.dataset_resolver = DatasetResolver(session)
            self.tag_resolver = TagResolver(session)
            self.sample_resolver = SampleResolver(session)
            self.annotation_resolver = AnnotationResolver(session)
            self.annotation_label_resolver = AnnotationLabelResolver(session)

    def _create_dataset(self, name: str, directory: str) -> None:
        """Creates a new dataset."""
        with db_manager.session() as session:  # noqa: F841
            # Create dataset record
            dataset = DatasetInput(
                name=name,
                directory=directory,
            )
            self._dataset = self.dataset_resolver.create(dataset)

    def _load_into_dataset(  # noqa: C901
        self, input_labels: ObjectDetectionInput, img_dir: Path
    ) -> None:
        """Store a loaded dataset in database."""
        if self._dataset is None:
            raise ValueError("Dataset must be created before loading data")

        label_map = {}
        for category in tqdm(
            input_labels.get_categories(),
            desc="Processing categories",
            unit=" categories",
        ):
            label = AnnotationLabelInput(annotation_label_name=category.name)
            stored_label = self.annotation_label_resolver.create(label)
            label_map[category.id] = stored_label.annotation_label_id

        annotations_to_create = []

        # temporary hack; create dummy tags until we can create tags
        tag_even = self.tag_resolver.create(
            TagInput(
                dataset_id=self._dataset.dataset_id,
                name="sample_even",
                kind="sample",
            )
        )
        tag_mod5 = self.tag_resolver.create(
            TagInput(
                dataset_id=self._dataset.dataset_id,
                name="sample_mod5",
                kind="sample",
            )
        )
        tag_annotation_random = self.tag_resolver.create(
            TagInput(
                dataset_id=self._dataset.dataset_id,
                name="anno_random",
                kind="annotation",
            )
        )

        # Process images and annotations
        for i, image_data in enumerate(
            tqdm(
                input_labels.get_labels(),
                desc="Processing images",
                unit=" images",
            )
        ):
            # Create sample record
            sample = SampleInput(
                file_name=str(image_data.image.filename),
                file_path_abs=str(img_dir / image_data.image.filename),
                width=image_data.image.width,
                height=image_data.image.height,
                dataset_id=self._dataset.dataset_id,
            )
            stored_sample = self.sample_resolver.create(sample)

            # temporary hack; create dummy tags until we can create tags
            if (i % 2) == 0:
                self.tag_resolver.add_tag_to_sample(
                    tag_even.tag_id, stored_sample
                )
            if (i % 5) == 0:
                self.tag_resolver.add_tag_to_sample(
                    tag_mod5.tag_id, stored_sample
                )

            # Create annotations
            for obj in image_data.objects:
                box = obj.box.to_format(BoundingBoxFormat.XYWH)
                x, y, width, height = box

                annotations_to_create.append(
                    AnnotationInput(
                        dataset_id=self._dataset.dataset_id,
                        sample_id=stored_sample.sample_id,
                        annotation_label_id=label_map[obj.category.id],
                        x=x,
                        y=y,
                        width=width,
                        height=height,
                    )
                )

            if len(annotations_to_create) >= ANNOTATION_BATCH_SIZE:
                self.annotation_resolver.create_many(annotations_to_create)
                annotations_to_create = []

            # temporary hack; create dummy tags until we can create tags
            sample_reloaded = self.sample_resolver.get_by_id(
                stored_sample.sample_id
            )
            if sample_reloaded and sample_reloaded.annotations:
                self.tag_resolver.add_tag_to_annotation(
                    tag_annotation_random.tag_id,
                    sample_reloaded.annotations[0],
                )

        # Insert any remaining annotations
        if annotations_to_create:
            self.annotation_resolver.create_many(annotations_to_create)
            annotations_to_create = []

        # temporary hack; create dummy tags until we can create tags
        annotations = self.annotation_resolver.get_all()
        random_annotation_ids = []
        for i, annotation in enumerate(annotations):
            if (i % 10) == 0:
                random_annotation_ids.append(annotation.annotation_id)
        self.tag_resolver.add_annotation_ids_to_tag_id(
            tag_id=tag_annotation_random.tag_id,
            annotation_ids=random_annotation_ids,
        )

    def from_yolo(
        self, data_yaml_path: str, input_split: str = "train"
    ) -> tuple[YOLODatasetLoader, UUID]:
        """Load a dataset in YOLO format and store in database."""
        if not self._yolo_loader:
            self._yolo_loader = YOLODatasetLoader(data_yaml_path, input_split)
        self._create_dataset(
            Path(data_yaml_path).parent.name,
            str(Path(data_yaml_path).parent.absolute()),
        )
        assert self._dataset is not None, "Unexpected value None for dataset"

        # Load the dataset
        label_input = self._yolo_loader.load()
        # TODO(Kondrat 01/25): We need to expose images_dir from label_input
        img_dir = label_input._images_dir()  # noqa: SLF001
        self._load_into_dataset(label_input, img_dir)

        # TODO: we should not return internal state but use getters
        return self._yolo_loader, self._dataset.dataset_id

    def from_coco(
        self, annotations_json_path: str, input_images_folder: str
    ) -> tuple[COCODatasetLoader, UUID]:
        """Load a dataset in COCO format and store in database."""
        if not self._coco_loader:
            self._coco_loader = COCODatasetLoader(annotations_json_path)
        self._create_dataset(
            Path(annotations_json_path).parent.name,
            str(Path(annotations_json_path).parent.absolute()),
        )
        assert self._dataset is not None, "Unexpected value None for dataset"

        # Load the dataset
        label_input = self._coco_loader.load()
        img_dir = (
            Path(input_images_folder)
            if Path(input_images_folder).is_absolute()
            else Path(annotations_json_path).parent / input_images_folder
        )
        self._load_into_dataset(label_input, img_dir)
        return self._coco_loader, self._dataset.dataset_id

    def launch(self) -> None:
        """Launch the web interface for the loaded dataset."""
        server = Server(host=PURPLE_HOST, port=PURPLE_PORT)

        print(f"Opening URL: {APP_URL}")

        # We need to open browser before starting the server
        webbrowser.open_new(APP_URL)

        server.start()

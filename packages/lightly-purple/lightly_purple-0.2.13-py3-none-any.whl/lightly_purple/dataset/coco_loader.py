"""YOLO dataset loader implementation."""

from pathlib import Path
from typing import Optional

from labelformat.formats import COCOObjectDetectionInput


class COCODatasetLoader:
    """Loader for COCO format datasets."""

    def __init__(self, annotations_json_path: str):
        """Initialize the COCO dataset loader.

        Args:
            annotations_json_path: Path to the annotations JSON file
        """
        self.annotations_json_path = Path(annotations_json_path)
        self._label_input: Optional[COCOObjectDetectionInput] = None

    def load(self) -> COCOObjectDetectionInput:
        """Load the COCO dataset.

        Returns:
            COCOObjectDetectionInput: The loaded dataset
        """
        if not self._label_input:
            self._label_input = COCOObjectDetectionInput(
                input_file=self.annotations_json_path,
            )
        return self._label_input

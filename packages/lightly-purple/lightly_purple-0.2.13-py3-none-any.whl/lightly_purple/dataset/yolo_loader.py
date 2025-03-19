"""YOLO dataset loader implementation."""

from pathlib import Path
from typing import Optional

from labelformat.formats import YOLOv8ObjectDetectionInput


class YOLODatasetLoader:
    """Loader for YOLO format datasets."""

    def __init__(self, data_yaml_path: str, input_split: str):
        """Initialize the YOLO dataset loader.

        Args:
            data_yaml_path: Path to the YOLO data.yaml file
            input_split: The split to load (train, val, test)
        """
        self.data_yaml_path = Path(data_yaml_path)
        self.input_split = input_split
        self._label_input: Optional[YOLOv8ObjectDetectionInput] = None

    def load(self) -> YOLOv8ObjectDetectionInput:
        """Load the YOLO dataset.

        Returns:
            YOLOv8ObjectDetectionInput: The loaded dataset
        """
        if not self._label_input:
            self._label_input = YOLOv8ObjectDetectionInput(
                input_file=self.data_yaml_path,
                input_split=self.input_split,
            )
        return self._label_input

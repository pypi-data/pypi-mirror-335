"""Example of how to use the DatasetLoader class."""

import os

from lightly_purple import DatasetLoader

# Create a DatasetLoader instance
loader = DatasetLoader()

# Define the path to the dataset (folder containing data.yaml)
dataset_path = os.getenv("DATASET_PATH", "/path/to/your/yolo/dataset/data.yaml")

# Load YOLO dataset using data.yaml path
yolo_loader, dataset_id = loader.from_yolo(
    dataset_path,
    input_split=os.getenv("PURPLE_DATASET_SPLIT", "test"),
)

loader.launch()

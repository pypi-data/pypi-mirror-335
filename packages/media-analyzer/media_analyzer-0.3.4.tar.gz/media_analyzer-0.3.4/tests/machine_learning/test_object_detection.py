from pathlib import Path

import PIL
import pytest

from media_analyzer.machine_learning.object_detection.resnet_object_detection import (
    ResnetObjectDetection,
)


@pytest.mark.parametrize(
    ("image", "objects"),
    [
        ("tent.jpg", ["car"]),
        ("cluster.jpg", ["laptop"]),
    ],
)
def test_resnet_object_detection(
    assets_folder: Path,
    image: str,
    objects: list[str],
) -> None:
    """Test the ResnetObjectDetection."""
    detector = ResnetObjectDetection()
    pil_image = PIL.Image.open(assets_folder / image)
    detections = detector.detect_objects(pil_image)

    for target in objects:
        assert target in (obj.label for obj in detections)

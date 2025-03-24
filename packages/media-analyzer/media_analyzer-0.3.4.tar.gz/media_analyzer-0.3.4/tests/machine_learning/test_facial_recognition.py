from pathlib import Path

import numpy as np
from PIL import Image
from scipy.spatial.distance import cosine

from media_analyzer.machine_learning.facial_recognition.insight_facial_recognition import (
    InsightFacialRecognition,
)


def test_insight_facial_detection(assets_folder: Path) -> None:
    """Test the InsightFacialRecognition."""
    image = Image.open(assets_folder / "faces/faces.webp")
    facial_recognition = InsightFacialRecognition()

    faces = facial_recognition.get_faces(image)

    faces_amount = 15
    assert len(faces) == faces_amount


def test_insight_facial_recognition(assets_folder: Path) -> None:
    """Test the InsightFacialRecognition."""
    # Load images and initialize facial recognition
    facial_recognition = InsightFacialRecognition()
    faces = [
        facial_recognition.get_faces(Image.open(assets_folder / "faces" / file_name))[0]
        for file_name in ["face1_a.jpg", "face1_b.jpg", "face2_a.jpg", "face2_b.jpg"]
    ]

    walter = faces[:2]
    micheal = faces[2:]

    # Compare faces and assert relationships
    for face in faces:
        other_faces = [f for f in faces if f != face]
        closest_face = other_faces[
            np.argmin([cosine(face.embedding, other_face.embedding) for other_face in other_faces])
        ]
        if face in walter:
            assert closest_face in walter
        elif face in micheal:
            assert closest_face in micheal

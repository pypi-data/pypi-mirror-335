from pathlib import Path

from PIL import Image

from media_analyzer.machine_learning.classifier.clip_classifier import CLIPClassifier
from media_analyzer.machine_learning.embedding.clip_embedder import CLIPEmbedder


def test_classifier_with_none_embedder() -> None:
    """Test the CLIPClassifier without passing an embedder."""
    classifier = CLIPClassifier()
    assert isinstance(classifier.embedder, CLIPEmbedder)


def test_classifier(assets_folder: Path) -> None:
    """Test the CLIPClassifier."""
    embedder = CLIPEmbedder()
    classifier = CLIPClassifier(embedder)
    image = Image.open(assets_folder / "sunset.jpg")
    image_embedded = embedder.embed_image(image)
    is_sunset, _ = classifier.binary_classify_image(image_embedded, "sunset", "camping")
    assert is_sunset

    image = Image.open(assets_folder / "tent.jpg")
    image_embedded = embedder.embed_image(image)
    is_camping, _ = classifier.binary_classify_image(image_embedded, "camping", "sunset")
    assert is_camping

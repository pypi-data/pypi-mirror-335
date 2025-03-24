from pathlib import Path
from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray
from PIL import Image

from media_analyzer.machine_learning.embedding.clip_embedder import CLIPEmbedder


@pytest.fixture(name="setup_embedder")
def setup_embedder_fixture(
    assets_folder: Path,
) -> tuple[CLIPEmbedder, list[Image.Image], NDArray[Any]]:
    """Set up the CLIPEmbedder and images for testing."""
    embedder = CLIPEmbedder()

    # Load images and create embeddings
    tent_img = Image.open(assets_folder / "tent.jpg")
    cluster_img = Image.open(assets_folder / "cluster.jpg")
    sunset_img = Image.open(assets_folder / "sunset.jpg")
    images: list[Image.Image] = [tent_img, cluster_img, sunset_img]
    images_embedding = embedder.embed_images(images)

    return embedder, images, images_embedding


@pytest.mark.parametrize(
    ("query", "img_index"),
    [
        ("A sunset over naples.", 2),  # Index 2 corresponds to sunset_img
        ("A tent on a camping.", 0),  # Index 0 corresponds to tent_img
        (
            "A cluster of raspberry pis in front of a laptop.",
            1,
        ),  # Index 1 corresponds to cluster_img
    ],
)
def test_clip_embedder(
    setup_embedder: tuple[
        CLIPEmbedder,
        list[Image.Image],
        NDArray[Any],
    ],
    query: str,
    img_index: int,
) -> None:
    """Test the CLIPEmbedder."""
    embedder, _, images_embedding = setup_embedder

    text_embedding = embedder.embed_text(query)
    # Calculate cosine similarities between text and each image
    similarities = images_embedding @ np.array(text_embedding)
    # Assert the highest similarity index matches the expected image index
    assert np.argmax(similarities).item() == img_index

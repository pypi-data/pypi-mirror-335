from pathlib import Path

import pytest
from PIL import Image

from media_analyzer.machine_learning.caption.blip_captioner import BlipCaptioner


@pytest.mark.cuda
def test_blip_captioner(
    assets_folder: Path,
) -> None:
    """Test the BlipCaptioner."""
    image = Image.open(assets_folder / "sunset.jpg")
    blip = BlipCaptioner()
    caption = blip.caption(image)
    assert isinstance(caption, str)
    min_caption_length = 3
    assert len(caption) > min_caption_length


@pytest.mark.cuda
def test_blip_captioner_conditional(
    assets_folder: Path,
) -> None:
    """Test the BlipCaptioner with a conditional caption."""
    image = Image.open(assets_folder / "sunset.jpg")
    blip = BlipCaptioner()
    caption = blip.caption(image, "A photo of ")
    assert isinstance(caption, str)
    min_caption_length = 3
    assert len(caption) > min_caption_length

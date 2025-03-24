from pathlib import Path

from PIL import Image

from media_analyzer.data.anaylzer_config import AnalyzerSettings
from media_analyzer.machine_learning.ocr.resnet_tesseract_ocr import ResnetTesseractOCR


def test_resnet_tesseract_ocr_text(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the getting text from an image with ResnetTesseractOCR."""
    image = Image.open(assets_folder / "ocr.jpg")
    ocr = ResnetTesseractOCR()
    has_text = ocr.has_legible_text(image)
    assert has_text

    extracted_text = ocr.get_text(image, default_config.media_languages)
    assert "SPAGHETTI" in extracted_text.upper()


def test_resnet_tesseract_ocr_boxes(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the getting text bounding boxes from an image with ResnetTesseractOCR."""
    image = Image.open(assets_folder / "ocr.jpg")
    ocr = ResnetTesseractOCR()

    boxes = ocr.get_boxes(image, default_config.media_languages)
    required_boxes_amount = 50
    assert len(boxes) > required_boxes_amount
    found_spaghetti = False
    for box in boxes:
        if "SPAGHETTI" in box.text:
            found_spaghetti = True
            break
    assert found_spaghetti

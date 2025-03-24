from collections import defaultdict
from pathlib import Path
from unittest.mock import patch

import pytest
from exiftool.exceptions import ExifToolExecuteError

from media_analyzer.data.anaylzer_config import AnalyzerSettings, FullAnalyzerConfig
from media_analyzer.data.enums.analyzer_module import FileModule, VisualModule
from media_analyzer.data.interfaces.api_io import InputMedia
from media_analyzer.media_analyzer import MediaAnalyzer


def test_media_analyzer_none_settings() -> None:
    """Test the MediaAnalyzer with no settings."""
    analyzer = MediaAnalyzer()
    assert isinstance(analyzer.config, FullAnalyzerConfig)


@pytest.mark.parametrize(
    ("photo_filename", "expect_gps", "expect_gif"),
    [
        pytest.param("cat_bee.gif", False, True),
        pytest.param("tent.jpg", True, False),
        pytest.param("sunset.jpg", True, False),
        pytest.param("ocr.jpg", False, False),
        pytest.param("faces/face2_b.jpg", False, False),
    ],
)
def test_media_analyzer(
    assets_folder: Path,
    default_config: AnalyzerSettings,
    photo_filename: str,
    expect_gps: bool,
    expect_gif: bool,
) -> None:
    """Test the MediaAnalyzer functionality for images with and without GPS data."""
    mock_caption_text = "A mock caption."
    with patch(
        "media_analyzer.machine_learning.caption.blip_captioner.BlipCaptioner.raw_caption"
    ) as mock_raw_caption:
        mock_raw_caption.return_value = mock_caption_text
        analyzer = MediaAnalyzer(default_config)
        result = analyzer.photo(assets_folder / photo_filename)

    assert len(result.frame_data) == 1

    assert result.image_data.exif is not None
    assert result.image_data.data_url is not None
    assert result.image_data.time is not None

    if expect_gps:
        assert result.image_data.gps is not None
        assert result.image_data.weather is not None
    else:
        assert result.image_data.gps is None
        assert result.image_data.weather is None

    if expect_gif:
        assert result.image_data.exif.gif is not None
    else:
        assert result.image_data.exif.gif is None


def test_video_analysis(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for a video."""
    mock_caption_text = "A mock caption."
    with patch(
        "media_analyzer.machine_learning.caption.blip_captioner.BlipCaptioner.raw_caption"
    ) as mock_raw_caption:
        mock_raw_caption.return_value = mock_caption_text
        analyzer = MediaAnalyzer(default_config)
        result = analyzer.analyze(
            InputMedia(
                path=assets_folder / "video" / "car.webm",
                frames=[
                    assets_folder / "video" / "frame1.jpg",
                    assets_folder / "video" / "frame2.jpg",
                ],
            )
        )

    frame_count = 2
    assert len(result.frame_data) == frame_count

    assert result.image_data.exif is not None
    assert result.image_data.exif.matroska is not None
    assert result.image_data.data_url is not None
    assert result.image_data.time is not None


def test_png_image(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for a png image."""
    default_config.enabled_file_modules = {FileModule.EXIF, FileModule.DATA_URL, FileModule.TIME}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "png_image.png")

    assert result.image_data.exif is not None
    assert result.image_data.data_url is not None
    assert result.image_data.time is not None


def test_photosphere(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for a photosphere."""
    default_config.enabled_file_modules = {FileModule.TAGS}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "photosphere.jpg")

    assert result.image_data.tags is not None
    assert result.image_data.tags.is_photosphere
    assert result.image_data.tags.use_panorama_viewer
    assert result.image_data.tags.projection_type == "equirectangular"
    assert not result.image_data.tags.is_night_sight


def test_night_sight(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for a night sight photo."""
    default_config.enabled_file_modules = {FileModule.TAGS}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "night_sight/PXL_20250104_170020532.NIGHT.jpg")

    assert result.image_data.tags is not None
    assert result.image_data.tags.is_night_sight
    assert not result.image_data.tags.is_photosphere
    assert not result.image_data.tags.use_panorama_viewer


def test_burst(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for burst photos."""
    default_config.enabled_file_modules = {FileModule.TAGS}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    results = [analyzer.photo(p) for p in (assets_folder / "burst").iterdir()]

    grouped = defaultdict(list)
    for result in results:
        assert result.image_data.tags is not None
        assert result.image_data.tags.is_burst
        grouped[result.image_data.tags.burst_id].append(result)

    print(grouped)
    expected_group_count = 3
    assert len(grouped) == expected_group_count
    expected_max_group_size = 5
    assert max(len(group) for group in grouped.values()) == expected_max_group_size
    assert "20150813_160421" in grouped


def test_motion(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for motion photos."""
    default_config.enabled_file_modules = {FileModule.TAGS}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "motion/PXL_20250103_180944831.MP.jpg")

    assert result.image_data.tags is not None
    assert result.image_data.tags.is_motion_photo
    assert isinstance(result.image_data.tags.motion_photo_presentation_timestamp, int)


def test_slowmotion(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for slowmotion video."""
    default_config.enabled_file_modules = {FileModule.TAGS}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "slowmotion.mp4")

    assert result.image_data.tags is not None
    assert result.image_data.tags.is_slowmotion
    assert result.image_data.tags.capture_fps == pytest.approx(120)


def test_timelapse(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for slowmotion video."""
    default_config.enabled_file_modules = {FileModule.TAGS}
    default_config.enabled_visual_modules = set()

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "timelapse.mp4")

    assert result.image_data.tags is not None
    assert result.image_data.tags.is_timelapse


def test_color_module(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer functionality for slowmotion video."""
    default_config.enabled_file_modules = set()
    default_config.enabled_visual_modules = {VisualModule.COLOR}

    analyzer = MediaAnalyzer(default_config)
    result = analyzer.photo(assets_folder / "sunset.jpg")

    assert result.frame_data[0].color
    color = result.frame_data[0].color
    assert len(color.prominent_colors) > 0
    assert len(color.themes) == len(color.prominent_colors)
    assert color.average_hue
    assert color.average_lightness
    assert color.average_saturation
    assert len(color.histogram["channels"]["red"]) == color.histogram["bins"]
    assert isinstance(color.themes[0], dict)


def test_exif_invalid_image(assets_folder: Path, default_config: AnalyzerSettings) -> None:
    """Test the MediaAnalyzer exif module for invalid jpeg file."""
    default_config.enabled_file_modules = {FileModule.EXIF}
    default_config.enabled_visual_modules = set()
    analyzer = MediaAnalyzer(default_config)
    with pytest.raises(ExifToolExecuteError):
        analyzer.photo(assets_folder / "invalid_image.png")
    with pytest.raises(ValueError, match="Media-analyzer does not support this file"):
        analyzer.photo(assets_folder / "text_file.txt")

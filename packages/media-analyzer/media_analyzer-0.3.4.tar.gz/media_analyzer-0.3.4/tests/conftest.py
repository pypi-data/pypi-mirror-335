from pathlib import Path

import pytest

from media_analyzer.data.anaylzer_config import AnalyzerSettings


@pytest.fixture
def assets_folder() -> Path:
    """Return the path to the assets folder."""
    return Path(__file__).parent / "assets"


@pytest.fixture
def default_config() -> AnalyzerSettings:
    """Return a default instance of AnalyzerSettings."""
    return AnalyzerSettings()

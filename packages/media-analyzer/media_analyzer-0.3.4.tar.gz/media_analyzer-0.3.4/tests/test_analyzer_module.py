import pytest

from media_analyzer.data.enums.analyzer_module import FileModule, VisualModule, analyzer_module


def test_analyzer_module() -> None:
    """Test str -> AnalyzerModule function."""
    for f_module in FileModule:
        assert analyzer_module(str(f_module)) == f_module
    for v_module in VisualModule:
        assert analyzer_module(str(v_module)) == v_module

    with pytest.raises(ValueError, match="is not a valid AnalyzerModule"):
        analyzer_module("test")

from media_analyzer.data.anaylzer_config import FullAnalyzerConfig
from media_analyzer.data.interfaces.frame_data import FrameData
from media_analyzer.processing.pipeline.pipeline_module import PipelineModule


class CaptionModule(PipelineModule[FrameData]):
    """Generate a caption from an image."""

    def process(self, data: FrameData, config: FullAnalyzerConfig) -> None:
        """Generate a caption from an image."""
        data.caption = config.captioner.caption(data.image)

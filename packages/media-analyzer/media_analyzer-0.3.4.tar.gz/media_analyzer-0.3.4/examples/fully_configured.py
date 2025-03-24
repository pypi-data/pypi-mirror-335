from pathlib import Path

from media_analyzer import MediaAnalyzer, AnalyzerSettings, CaptionerProvider, LLMProvider

config = AnalyzerSettings(
    media_languages=("eng",),
    captions_provider=CaptionerProvider.MINICPM,
    llm_provider=LLMProvider.MINICPM,
    enable_text_summary=True,
    enable_document_summary=True,
    document_detection_threshold=50,
    face_detection_threshold=0.5,
    # You can turn off modules by selecting only the ones you need:
    # enabled_file_modules={"ExifModule"},
    # enabled_visual_modules={"CaptionModule"},
)
analyzer = MediaAnalyzer(config=config)
media_file = Path(__file__).parents[1] / "tests/assets/tent.jpg"
result = analyzer.photo(media_file)
print(result)

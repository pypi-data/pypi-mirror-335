from pathlib import Path

from media_analyzer import MediaAnalyzer, AnalyzerSettings
from media_analyzer.data.enums.analyzer_module import FileModule, VisualModule

config = AnalyzerSettings(
    enabled_file_modules={FileModule.EXIF},  # Only do exif data analysis on file
    enabled_visual_modules={VisualModule.CAPTION},  # Only do caption module as visual module
)
analyzer = MediaAnalyzer(config=config)
media_file = Path(__file__).parents[1] / "tests/assets/tent.jpg"
result = analyzer.photo(media_file)

print(result)

# Result (converted to json):
# {
#   "image_data": {
#     "exif": {
#       "width": 5312,
#       "height": 2988,
#       ...
#     },
#     "dataurl": null,
#     "gps": null,
#     "time": null,
#     "weather": null
#   },
#   "frame_data": [
#     {
#       "ocr": null,
#       "embedding": null,
#       "faces": null,
#       "summary": null,
#       "caption": "There is a car parked next to a tent with a lot of luggage",
#       "objects": null,
#       "classification": null,
#       "measured_quality": null
#     }
#   ]
# }

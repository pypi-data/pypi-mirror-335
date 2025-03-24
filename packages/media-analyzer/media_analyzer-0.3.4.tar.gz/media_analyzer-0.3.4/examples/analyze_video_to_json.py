import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any

from media_analyzer import InputMedia, MediaAnalyzer

analyzer = MediaAnalyzer()
video_file = Path(__file__).parents[1] / "tests/assets/video/car.webm"
# To analyze a video you need to supply some snapshot images from the video
frames = [
    Path(__file__).parents[1] / f"tests/assets/video/{frame}" for frame in
    ["frame1.jpg", "frame2.jpg"]
]
result = analyzer.analyze(InputMedia(path=video_file, frames=frames))


# Serialize result to json
def custom_serializer(obj: Any) -> str:
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


print(json.dumps(asdict(result), indent=2, default=custom_serializer))

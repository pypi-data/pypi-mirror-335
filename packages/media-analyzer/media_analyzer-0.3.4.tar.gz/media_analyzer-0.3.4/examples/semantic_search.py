from pathlib import Path

import numpy as np
from scipy.spatial.distance import cosine

from media_analyzer import MediaAnalyzer, AnalyzerSettings
from media_analyzer.data.enums.analyzer_module import VisualModule

photo_filenames = ["cluster.jpg", "sunset.jpg", "tent.jpg"]
photos = [Path(__file__).parents[1] / "tests/assets" / name for name in photo_filenames]

analyzer = MediaAnalyzer(config=AnalyzerSettings(
    enabled_file_modules=set(),
    enabled_visual_modules={VisualModule.EMBEDDING},  # We only need embedding module
))
results = [analyzer.photo(photo) for photo in photos]
image_embeddings = [np.array(result.frame_data[0].embedding) for result in results]


def search(query_str: str) -> str:
    query_embedding = analyzer.config.embedder.embed_text(query_str)  # pylint: disable=E1111
    similarities = [1 - cosine(query_embedding, embedding) for embedding in image_embeddings]
    most_similar_index = np.argmax(similarities)
    return photo_filenames[most_similar_index]


query = "A campsite with a car and a tent."
print(f"Image closest to the query '{query}' is:")
print(search(query))
# > tent.jpg

query = "A sunset overlooking a city."
print(f"Image closest to the query '{query}' is:")
print(search(query))
# > sunset.jpg

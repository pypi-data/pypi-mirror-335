from functools import lru_cache
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy.special import softmax
from sklearn.metrics.pairwise import cosine_similarity

from media_analyzer.machine_learning.classifier.base_classifier import BaseClassifier
from media_analyzer.machine_learning.embedding.clip_embedder import CLIPEmbedder
from media_analyzer.machine_learning.embedding.embedder_protocol import EmbedderProtocol


class CLIPClassifier(BaseClassifier):
    """Classifier implementation using the CLIP model."""

    embedder: EmbedderProtocol

    def __init__(self, embedder: EmbedderProtocol | None = None) -> None:
        """Initialize the CLIP classifier.

        Args:
            embedder: The embedder to use for text embedding.
        """
        if embedder is None:
            embedder = CLIPEmbedder()
        self.embedder = embedder

    @lru_cache
    def _cached_embed_text(self, text: str) -> NDArray[Any]:
        """Embed the given text and cache the result.

        Args:
            text: The text to embed.

        Returns:
            The text embedding.
        """
        return self.embedder.embed_text(text)

    def classify_image(
        self,
        image_embedding: NDArray[Any],
        classes: list[str],
    ) -> tuple[int, float]:
        """Classify the image embedding into one of the given classes.

        Args:
            image_embedding: The image embedding to classify.
            classes: The list of classes to classify the image into.

        Returns:
            The index of the best class and the confidence score.
        """
        text_embeddings = [self._cached_embed_text(c) for c in classes]
        similarities = cosine_similarity([image_embedding], text_embeddings)
        normalized: NDArray[Any] = softmax(similarities)
        best_index = np.argmax(normalized)
        confidence = normalized[0, best_index].item()
        return int(best_index), confidence

    def binary_classify_image(
        self,
        image_embedding: NDArray[Any],
        positive_prompt: str,
        negative_prompt: str,
    ) -> tuple[bool, float]:
        """Binary classify the image embedding based on the given prompts.

        Args:
            image_embedding: The image embedding to classify.
            positive_prompt: The positive prompt for the classification.
            negative_prompt: The negative prompt for the classification.

        Returns:
            A tuple containing the classification result and the confidence score.
        """
        index, confidence = self.classify_image(
            image_embedding,
            [negative_prompt, positive_prompt],
        )
        return bool(index), confidence

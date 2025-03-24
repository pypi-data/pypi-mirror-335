from abc import ABC, abstractmethod
from enum import Enum, StrEnum
from typing import Any, TypeVar

from numpy.typing import NDArray

TStrEnum = TypeVar("TStrEnum", bound=StrEnum)
TEnum = TypeVar("TEnum", bound=Enum)


class BaseClassifier(ABC):
    """Base classifier class."""

    @abstractmethod
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

    @abstractmethod
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

    def classify_to_enum_with_descriptions(
        self,
        image_embedding: NDArray[Any],
        positive_prompt: str | None,
        negative_prompt: str | None,
        class_descriptions: dict[TEnum, str],
    ) -> TEnum | None:
        """Classify the image embedding into an enum based on the given descriptions.

        Args:
            image_embedding: The image embedding to classify.
            positive_prompt: The positive prompt for the classification.
            negative_prompt: The negative prompt for the classification.
            class_descriptions: The dictionary of enum values and their descriptions.

        Returns:
            The enum value of the best class or None if the classification failed.
        """
        if positive_prompt is not None and negative_prompt is not None:
            is_enum, _ = self.binary_classify_image(
                image_embedding,
                positive_prompt,
                negative_prompt,
            )
            if not is_enum:
                return None

        best_index, _ = self.classify_image(
            image_embedding,
            list(class_descriptions.values()),
        )
        return list(class_descriptions.keys())[best_index]

    def classify_to_enum(
        self,
        image_embedding: NDArray[Any],
        positive_prompt: str,
        negative_prompt: str,
        enum_type: type[TStrEnum],
    ) -> TStrEnum | None:
        """Classify the image embedding into an enum based on the given enum type.

        Args:
            image_embedding: The image embedding to classify.
            positive_prompt: The positive prompt for the classification.
            negative_prompt: The negative prompt for the classification.
            enum_type: The enum type to classify the image into.

        Returns:
            The enum value of the best class or None if the classification failed.
        """
        is_enum, _ = self.binary_classify_image(
            image_embedding,
            positive_prompt,
            negative_prompt,
        )
        if not is_enum:
            return None

        best_index, _ = self.classify_image(
            image_embedding,
            [e.value.replace("_", " ") for e in enum_type],
        )
        return list(enum_type)[best_index]

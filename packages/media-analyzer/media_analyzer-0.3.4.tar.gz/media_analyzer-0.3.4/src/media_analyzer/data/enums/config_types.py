from enum import StrEnum, auto


class LLMProvider(StrEnum):
    """LLM providers enum."""

    MINICPM = auto()
    OPENAI = auto()


class CaptionerProvider(StrEnum):
    """Captioner providers enum."""

    MINICPM = auto()
    OPENAI = auto()
    BLIP = auto()

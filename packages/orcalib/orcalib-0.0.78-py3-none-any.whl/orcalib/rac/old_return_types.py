"""Common type definitions and utility functions for the RAC module."""

from dataclasses import dataclass

import numpy as np

from orcalib.memoryset import LabeledMemoryLookup


@dataclass
class PredictionResult:
    """
    The result of a single prediction.
    """

    label: int
    """The predicted label."""

    label_name: str | None
    """The name of the predicted label."""

    confidence: float
    """The confidence of the prediction."""

    memories: list[LabeledMemoryLookup]
    """The memory lookups that were used to guide this prediction."""

    logits: np.ndarray
    """The logits of the prediction."""

    input_embedding: np.ndarray
    """The embedding of the input."""

    def __repr__(self) -> str:
        label = f"<{self.label_name}: {str(self.label)}>" if self.label_name else str(self.label)
        return (
            "PredictionResult("
            f"label={label}, "
            f"confidence={self.confidence:.4f}, "
            f"memories=<list.LabeledMemoryLookupResult({len(self.memories)})>, "
            f"logits=<array.{self.logits.dtype}{self.logits.shape}>, "
            f"input_embedding=<array.{self.input_embedding.dtype}{self.input_embedding.shape}>)"
        )


@dataclass
class EvalResult:
    f1: float
    roc_auc: float | None
    accuracy: float
    loss: float

    def __repr__(self) -> str:
        return f"EvalResult({', '.join([f'{k}={v:.4f}' for k, v in self.__dict__.items() if v is not None])})"


@dataclass
class LabeledMemoryLookupStats:
    correct: int
    incorrect: int
    label: int | None
    ratio: float | None
    total: int | None


@dataclass
class AnalyzePrediction:
    label: int
    logits: list[float]
    confidence: float


@dataclass
class AnalyzeResult:
    num_memories_accessed: int
    label_counts: dict[int, int]
    label_stats: list[dict]
    memory_stats: list[dict]
    mean_memory_lookup_score: float
    prediction: AnalyzePrediction

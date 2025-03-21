import logging
from collections import Counter

import numpy as np
import torch
from sklearn.metrics import f1_score, roc_auc_score

from ..memoryset import InputType
from .old_return_types import (
    AnalyzePrediction,
    AnalyzeResult,
    EvalResult,
    LabeledMemoryLookupStats,
    PredictionResult,
)
from .visualization import visualize_memory_stats


def compute_prediction_metrics(preds: list[tuple[int, np.ndarray]], correct_labels) -> EvalResult:
    logger = logging.getLogger(__name__)
    predicted_labels = [pred[0] for pred in preds]
    labels_w_confidence = [pred[1] for pred in preds]
    num_labels = len(correct_labels)
    num_classes_y_true = len(np.unique(correct_labels))
    f1 = f1_score(correct_labels, predicted_labels, average="binary" if num_classes_y_true == 2 else "weighted")
    num_classes_y_score = len(labels_w_confidence[1])
    accuracy = sum([c == p for c, p in zip(correct_labels, predicted_labels)]) / num_labels
    loss = float(torch.nn.CrossEntropyLoss()(torch.tensor(labels_w_confidence), torch.tensor(correct_labels)))
    # Compute roc_auc_score only if all classes are present
    if num_classes_y_true == num_classes_y_score:
        # binary classification requires a list of probabilities for only the positive class
        if num_classes_y_true == 2:
            auc = float(
                roc_auc_score(
                    correct_labels, [label[1] / sum(label) for label in labels_w_confidence], multi_class="ovr"
                )
            )
        else:
            auc = float(roc_auc_score(correct_labels, labels_w_confidence, multi_class="ovr"))
    else:
        logger.info("Warning: Not all classes are present in the correct_labels. Add more test data to calculate AUC.")
        auc = None
    if isinstance(f1, float):
        return EvalResult(f1=f1, roc_auc=auc, accuracy=accuracy, loss=loss)
    else:
        raise ValueError(f"Error computing metrics: f1 is not a float: {f1}")


def aggregate_memory_stats(
    results: list[PredictionResult], dataset: list[tuple[InputType, int]], plot: bool
) -> dict[str, LabeledMemoryLookupStats]:
    logger = logging.getLogger(__name__)
    memory_stats: dict[str, LabeledMemoryLookupStats] = {}
    for i, result in enumerate(results):
        correct_label = dataset[i][1]
        for memory in result.memories:
            memory_id = memory.memory_id
            if memory_id is not None:
                if memory_id in memory_stats:
                    # Does the memory agree with the correct label?
                    if memory.label == correct_label:
                        memory_stats[str(memory_id)].correct = memory_stats[str(memory_id)].correct + 1
                    else:
                        memory_stats[str(memory_id)].incorrect = memory_stats[str(memory_id)].incorrect + 1
                else:
                    memory_stats[str(memory_id)] = LabeledMemoryLookupStats(
                        correct=int(memory.label == correct_label),
                        incorrect=int(memory.label != correct_label),
                        label=(
                            memory.label
                            if type(memory.label) is int
                            else memory.label[0]  # type: ignore - this will either be an int or a tuple
                        ),
                        ratio=None,
                        total=None,
                    )

                for memory_id, stats in memory_stats.items():
                    stats.total = stats.correct + stats.incorrect
                    stats.ratio = stats.correct / stats.total if stats.total > 0 else 0
            else:
                logger.info("A memory was found with no ID. Memory stats will not be aggregated.")
                return {}

    visualize_memory_stats(memory_stats) if plot else None
    return memory_stats


def analyze_result(result: PredictionResult) -> AnalyzeResult:
    """Analyzes the result of a prediction, returning a dictionary of statistics on labels and accessed memories"""
    memory_stats = []
    label_counts_tuple = []
    for memory in result.memories:
        memory_stat = {
            "label": memory.label,
            "label_name": memory.label_name,
            "lookup_score": memory.lookup_score,
            "memory_value": memory.value,
            "memory_id": memory.memory_id,
        }
        memory_stats.append(memory_stat)
        label_tuple = (memory.label, memory.label_name)
        label_counts_tuple.append(label_tuple)
    label_counts = Counter(label[0] for label in label_counts_tuple)
    label_names = {label[0]: label[1] for label in label_counts_tuple}
    labels = [int(key) for key in label_counts.keys() if isinstance(key, int)]
    label_stats = [
        {
            "label": label,
            "label_name": label_names.get(label, "Unknown"),
            "count": sum(memory.label == label for memory in result.memories),
            "variance": np.var(
                [
                    memory.lookup_score
                    for memory in result.memories
                    if memory.label == label and memory.lookup_score is not None
                ]
            ),
            "mean": np.mean(
                [
                    memory.lookup_score
                    for memory in result.memories
                    if memory.label == label and memory.lookup_score is not None
                ]
            ),
        }
        for label in labels
    ]

    return AnalyzeResult(
        num_memories_accessed=len(result.memories),
        label_counts=label_counts,
        label_stats=label_stats,
        memory_stats=memory_stats,
        mean_memory_lookup_score=float(
            np.mean([memory.lookup_score for memory in result.memories if memory.lookup_score is not None])
        ),
        prediction=AnalyzePrediction(label=result.label, logits=result.logits.tolist(), confidence=result.confidence),
    )

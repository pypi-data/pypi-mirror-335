from __future__ import annotations

import logging
from contextlib import contextmanager
from datetime import datetime, timezone
from enum import Enum
from tempfile import TemporaryDirectory
from typing import Callable, Literal, cast, overload

import numpy as np
import torch
from datasets import Dataset
from numpy.typing import NDArray
from pydantic import UUID4, BaseModel
from sklearn.metrics import (
    accuracy_score,
    auc,
    explained_variance_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    roc_auc_score,
)
from torch import Tensor, nn
from tqdm.auto import trange
from transformers import (
    AutoConfig,
    AutoModelForImageClassification,
    AutoModelForSequenceClassification,
    PretrainedConfig,
    PreTrainedModel,
)
from transformers.modeling_outputs import SequenceClassifierOutput
from uuid_utils.compat import uuid4

from ..dataset_utils import parse_dataset
from ..fs_utils import download_dir, is_using_blob_storage, upload_dir
from ..memoryset import (
    InputType,
    InputTypeList,
    LabeledMemoryLookup,
    LabeledMemoryset,
    ScoredMemoryLookup,
    ScoredMemoryset,
)
from ..memoryset.memory_types import LabeledMemoryLookupColumnResult, ScoredMemoryLookupColumnResult
from ..metrics import calculate_pr_curve, calculate_roc_curve
from ..progress_utils import OnLogCallback, OnProgressCallback
from ..pydantic_utils import Vector
from ..torch_layers import (
    BalancedMemoryMixtureOfExpertsClassificationHead,
    FeedForwardClassificationHead,
    MemoryMixtureOfExpertsClassificationHead,
    MemoryMixtureOfExpertsRegressionHead,
    NearestMemoriesClassificationHead,
)
from .model_finetuning import RACTrainingArguments, finetune


class LabelPredictionResult(BaseModel):
    """Predicted label and confidence for a single input."""

    prediction_id: UUID4
    """The unique ID to identify this prediction"""

    label: int
    """The predicted label."""

    label_name: str | None
    """The name of the predicted label."""

    confidence: float
    """The confidence of the prediction."""

    anomaly_score: float | None
    """The score for how anomalous the input is relative to the memories."""

    def __repr__(self) -> str:
        label = f"<{self.label_name}: {str(self.label)}>" if self.label_name else str(self.label)
        return f"LabelPredictionResult(label={label}, confidence={self.confidence:.4f})"


class LabelPrediction(LabelPredictionResult):
    """Full details about a single label prediction."""

    timestamp: datetime
    """The time when the prediction was requested"""

    logits: Vector
    """The logits of the prediction."""

    input_value: InputType
    """The input to the model."""

    input_embedding: Vector
    """The embedding of the input."""

    expected_label: int | None
    """The expected label for the input, if available (e.g. during evaluation)"""


class LabelPredictionMemoryLookup(LabeledMemoryLookup):
    """Full information about the lookup of a single memory for a prediction."""

    prediction_id: UUID4
    """The unique ID of the prediction that this lookup was made for"""

    attention_weight: float
    """The attention the model gave to this memory lookup."""

    def __repr__(self) -> str:
        return "".join(
            [
                "LabeledMemoryLookup(\n",
                f"    value={(chr(39) + self.value + chr(39)) if isinstance(self.value, str) else '<Image>'},\n",
                f"    label={('<' + self.label_name + ': ' + str(self.label) + '>') if self.label_name else str(self.label)},\n",
                f"    metadata={self.metadata},\n" if self.metadata else "",
                f"    prediction_id={self.prediction_id},\n",
                f"    memory_id={self.memory_id},\n",
                f"    memory_version={self.memory_version},\n",
                f"    attention_weight={self.attention_weight},\n" if self.attention_weight else "",
                f"    lookup_score={self.lookup_score},\n",
                f"    embedding=<array.{self.embedding.dtype}{self.embedding.shape}>,\n",
                f"    reranker_score={self.reranker_score},\n" if self.reranker_score else "",
                (
                    f"    reranker_embedding=<array.{self.reranker_embedding.dtype}{self.reranker_embedding.shape}>,\n"
                    if self.reranker_embedding
                    else ""
                ),
                ")",
            ]
        )


class LabelPredictionWithMemories(LabelPrediction):
    """Result for a single prediction with full details and details of the memory lookups"""

    memories: list[LabelPredictionMemoryLookup]
    """The memory lookups that were used to guide this prediction."""

    def __repr__(self) -> str:
        return (
            "LabelPredictionWithMemories(\n"
            f"    label={('<' + self.label_name + ': ' + str(self.label) + '>') if self.label_name else str(self.label)},\n"
            f"    confidence={self.confidence:.4f},\n"
            f"    logits=<array.{self.logits.dtype}{self.logits.shape}>,\n"
            f"    input_embedding=<array.{self.input_embedding.dtype}{self.input_embedding.shape}>,\n"
            f"    memories=<list.LabelPredictionMemoryLookup({len(self.memories)})>,\n"
            ")"
        )


class ScorePredictionResult(BaseModel):
    """Predicted score and confidence for a single input."""

    prediction_id: UUID4
    """The unique ID to identify this prediction"""

    score: float
    """The predicted score."""

    confidence: float
    """The confidence of the prediction."""

    anomaly_score: float
    """The score for how anomalous the input is relative to the memories."""

    def __repr__(self) -> str:
        return f"ScoredPredictionResult(score={self.score}, confidence={self.confidence:.4f})"


class ScorePrediction(ScorePredictionResult):
    """Full details about a single score prediction."""

    timestamp: datetime
    """The time when the prediction was requested"""

    logits: float
    """The logits of the prediction."""

    input_value: InputType
    """The input to the model."""

    input_embedding: Vector
    """The embedding of the input."""

    expected_score: float | None
    """The expected score for the input, if available (e.g. during evaluation)"""


class ScorePredictionMemoryLookup(ScoredMemoryLookup):
    """Full information about the lookup of a single memory for a prediction."""

    prediction_id: UUID4
    """The unique ID of the prediction that this lookup was made for"""

    attention_weight: float
    """The attention the model gave to this memory lookup."""

    def __repr__(self) -> str:
        return "".join(
            [
                "ScoredMemoryLookup(\n",
                f"    value={(chr(39) + self.value + chr(39)) if isinstance(self.value, str) else '<Image>'},\n",
                f"    score={self.score},\n",
                f"    metadata={self.metadata},\n" if self.metadata else "",
                f"    prediction_id={self.prediction_id},\n",
                f"    memory_id={self.memory_id},\n",
                f"    memory_version={self.memory_version},\n",
                f"    attention_weight={self.attention_weight},\n" if self.attention_weight else "",
                f"    lookup_score={self.lookup_score},\n",
                f"    embedding=<array.{self.embedding.dtype}{self.embedding.shape}>,\n",
                f"    reranker_score={self.reranker_score},\n" if self.reranker_score else "",
                (
                    f"    reranker_embedding=<array.{self.reranker_embedding.dtype}{self.reranker_embedding.shape}>,\n"
                    if self.reranker_embedding
                    else ""
                ),
                ")",
            ]
        )


class ScorePredictionWithMemories(ScorePrediction):
    """Result for a single prediction with full details and details of the memory lookups"""

    memories: list[ScorePredictionMemoryLookup]
    """The memory lookups that were used to guide this prediction."""

    def __repr__(self) -> str:
        return (
            "ScoredPredictionWithMemories(\n"
            f"    score={self.score},\n"
            f"    confidence={self.confidence:.4f},\n"
            f"    logits={self.logits},\n"
            f"    input_embedding=<array.{self.input_embedding.dtype}{self.input_embedding.shape}>,\n"
            f"    memories=<list.ScoredPredictionMemoryLookup({len(self.memories)})>,\n"
            ")"
        )


class ClassificationEvaluationResult(BaseModel):
    f1_score: float
    """F1 score of the predictions"""

    accuracy: float
    """Accuracy of the predictions"""

    loss: float
    """Cross-entropy loss of the logits"""

    class PrecisionRecallCurve(BaseModel):
        thresholds: list[float]
        precisions: list[float]
        recalls: list[float]
        auc: float

        def __repr__(self) -> str:
            return (
                "PrecisionRecallCurve(\n"
                f"    thresholds={self.thresholds[0]:.4f}...{self.thresholds[-1]:.4f},\n"
                f"    precisions={self.precisions[0]:.4f}...{self.precisions[-1]:.4f},\n"
                f"    recalls={self.recalls[0]:.4f}...{self.recalls[-1]:.4f},\n"
                f"    auc={self.auc:.4f}\n"
            )

    precision_recall_curve: PrecisionRecallCurve | None
    """Precision-recall curve (only for binary classification)"""

    class ROCCurve(BaseModel):
        thresholds: list[float]
        false_positive_rates: list[float]
        true_positive_rates: list[float]
        auc: float

        def __repr__(self) -> str:
            return (
                "ROCCurve(\n"
                f"    thresholds={self.thresholds[0]:.4f}...{self.thresholds[-1]:.4f},\n"
                f"    false_positive_rates={self.false_positive_rates[0]:.4f}...{self.false_positive_rates[-1]:.4f},\n"
                f"    true_positive_rates={self.true_positive_rates[0]:.4f}...{self.true_positive_rates[-1]:.4f},\n"
                f"    auc={self.auc:.4f}\n"
            )

    roc_curve: ROCCurve | None
    """ROC curve (only for binary classification)"""

    def __repr__(self) -> str:
        return (
            "ClassificationEvaluationResult(\n"
            f"    f1_score={self.f1_score:.4f},\n"
            f"    accuracy={self.accuracy:.4f},\n"
            f"    loss={self.loss:.4f},\n"
            f"    precision_recall_curve={self.precision_recall_curve},\n"
            f"    roc_curve={self.roc_curve}\n"
            ")"
        )

    @staticmethod
    def calculate_metrics(
        *,
        logits_array: NDArray[np.float32],
        targets_array: NDArray[np.int64],
        predictions_array: NDArray[np.int64],
        total_loss: float,
    ) -> ClassificationEvaluationResult:
        # Compute metrics
        f1 = float(f1_score(targets_array, predictions_array, average="weighted"))
        accuracy = float(accuracy_score(targets_array, predictions_array))

        # Only compute ROC AUC and PR AUC for binary classification
        unique_classes = np.unique(targets_array)

        pr_curve = None
        roc_curve = None

        if len(unique_classes) == 2:
            try:
                precisions, recalls, pr_thresholds = calculate_pr_curve(targets_array, logits_array)
                pr_auc = float(auc(recalls, precisions))

                pr_curve = ClassificationEvaluationResult.PrecisionRecallCurve(
                    precisions=precisions.tolist(),
                    recalls=recalls.tolist(),
                    thresholds=pr_thresholds.tolist(),
                    auc=pr_auc,
                )

                fpr, tpr, roc_thresholds = calculate_roc_curve(targets_array, logits_array)
                roc_auc = float(roc_auc_score(targets_array, logits_array[:, 1]))

                roc_curve = ClassificationEvaluationResult.ROCCurve(
                    false_positive_rates=fpr.tolist(),
                    true_positive_rates=tpr.tolist(),
                    thresholds=roc_thresholds.tolist(),
                    auc=roc_auc,
                )
            except ValueError as e:
                logging.warning(f"Error calculating PR and ROC curves: {e}")

        total_samples = len(targets_array)

        return ClassificationEvaluationResult(
            f1_score=f1,
            accuracy=accuracy,
            loss=total_loss / total_samples,
            precision_recall_curve=pr_curve,
            roc_curve=roc_curve,
        )


class RegressionEvaluationResult(BaseModel):
    """Evaluation metrics for regression predictions."""

    mse: float
    """Mean squared error of the predictions"""

    rmse: float
    """Root mean squared error of the predictions"""

    mae: float
    """Mean absolute error of the predictions"""

    r2: float
    """R-squared score (coefficient of determination) of the predictions"""

    explained_variance: float
    """Explained variance score of the predictions"""

    loss: float
    """Mean squared error loss of the predictions"""

    def __repr__(self) -> str:
        return f"RegressionEvaluationResult({', '.join([f'{k}={v:.4f}' for k, v in self.__dict__.items() if v is not None])})"


class RACHeadType(str, Enum):
    KNN = "KNN"
    MMOE = "MMOE"
    FF = "FF"
    BMMOE = "BMMOE"


class RARHeadType(str, Enum):
    """Type of regression head to use in a RAR model."""

    MMOE = "mmoe"  # Memory mixture of experts regression


class RARModelConfig(PretrainedConfig):
    model_type = "rar-model"

    head_type: RARHeadType
    memoryset_uri: str | None
    memory_lookup_count: int | None
    weigh_memories: bool | None
    min_memory_weight: float | None
    num_layers: int | None
    dropout_prob: float | None

    def __init__(
        self,
        memoryset_uri: str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
        **kwargs,
    ):
        """
        Initialize the config

        Note:
            While all args of a pretrained config must be optional, `memoryset_uri` must be specified.

        Args:
            memoryset_uri: URI of the memoryset to use, this is required
            memory_lookup_count: Number of memories to lookup for each input, defaults to 10
            head_type: Type of regression head to use
            weigh_memories: Optional parameter for KNN head, whether to weigh memories by their lookup score
            min_memory_weight: Optional parameter for KNN head, minimum memory weight under which memories are ignored
            num_layers: Optional parameter for FF head, number of layers in the feed forward network
            dropout_prob: Optional parameter for FF head, dropout probability
        """
        # We cannot require memoryset_uri here, because this class must be initializable without
        # passing any parameters for the PretrainedConfig.save_pretrained method to work, so instead
        # we throw an error in the RetrievalAugmentedRegressor initializer if it is missing
        self.memoryset_uri = memoryset_uri
        self.memory_lookup_count = memory_lookup_count
        self.head_type = head_type if isinstance(head_type, RARHeadType) else RARHeadType(head_type)
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        super().__init__(**kwargs)


def _estimate_anomaly_score(
    lookup_res: ScoredMemoryLookupColumnResult | LabeledMemoryLookupColumnResult,
    idx: int,
) -> float:
    # Get index of memory with highest lookup score for this prediction
    memory_lookup_scores = lookup_res["memories_lookup_scores"][idx]
    if memory_lookup_scores.size == 0:
        return 1.0

    max_score_idx = np.argmax(memory_lookup_scores)

    # Get input embedding and corresponding top memory embedding
    input_emb = lookup_res["input_embeddings"][idx]
    top_memory_emb = lookup_res["memories_embeddings"][idx][max_score_idx]

    # Compute inner product between input and top memory embedding
    input_memory_similarity = float(np.inner(input_emb, top_memory_emb))

    if input_memory_similarity < 0:
        return 1.0
    else:
        return 1.0 - input_memory_similarity


class RARModel(PreTrainedModel):
    """A retrieval augmented regression model that uses a memoryset to make predictions."""

    config_class = RARModelConfig
    base_model_prefix = "rar"
    memory_lookup_count: int

    def _init_head(self):
        match self.config.head_type:
            case RARHeadType.MMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or 10
                self.head = MemoryMixtureOfExpertsRegressionHead(
                    embedding_dim=self.embedding_dim,
                )
            case _:
                raise ValueError(f"Unsupported head type: {self.config.head_type}")

    @overload
    def __init__(self, config: RARModelConfig):
        pass

    @overload
    def __init__(
        self,
        *,
        memoryset: ScoredMemoryset | str,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        pass

    def __init__(
        self,
        config: RARModelConfig | None = None,
        *,
        memoryset: ScoredMemoryset | str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RARHeadType | str = RARHeadType.MMOE,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        if config is None:
            assert memoryset is not None
            if isinstance(memoryset, ScoredMemoryset):
                self.memoryset = memoryset
            else:
                self.memoryset = ScoredMemoryset.connect(memoryset)
            config = RARModelConfig(
                memoryset_uri=self.memoryset.uri,
                memory_lookup_count=memory_lookup_count,
                head_type=head_type,
                weigh_memories=weigh_memories,
                min_memory_weight=min_memory_weight,
                num_layers=num_layers,
                dropout_prob=dropout_prob,
            )
        else:
            assert (
                memoryset is not None
                or memory_lookup_count is not None
                or head_type is not None
                or weigh_memories is not None
                or min_memory_weight is not None
                or num_layers is not None
                or dropout_prob is not None
            ), "Either config or kwargs can be provided, not both"
            if not config.memoryset_uri:
                # all configs must have defaults in a PretrainedConfig, but this one is required
                raise ValueError("memoryset_uri must be specified in config")
            self.memoryset = ScoredMemoryset.connect(config.memoryset_uri)
        super().__init__(config)
        self.embedding_dim = self.memoryset.embedding_model.embedding_dim
        self._init_head()
        self.criterion = nn.MSELoss()

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    def reset(self):
        """Reset the model weights to their initial state"""
        self._init_head()

    def attach(self, memoryset: ScoredMemoryset | str):
        """
        Attach a memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset
        """
        self.memoryset = memoryset if isinstance(memoryset, ScoredMemoryset) else ScoredMemoryset.connect(memoryset)

    def use(self, memoryset: ScoredMemoryset | str):
        """
        Temporarily attach a different memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset

        Examples:
            with model.use(memoryset):
                model.predict("test input")
        """

        @contextmanager
        def ctx_manager():
            previous_memoryset = self.memoryset
            try:
                self.attach(memoryset)
                yield
            finally:
                if previous_memoryset:
                    self.attach(previous_memoryset)

        return ctx_manager()

    def forward(
        self,
        input_embeddings: Tensor | None = None,
        memories_scores: Tensor | None = None,
        memories_embeddings: Tensor | None = None,
        memories_weights: Tensor | None = None,
        labels: Tensor | None = None,
    ) -> SequenceClassifierOutput:
        logits = self.head(input_embeddings, memories_scores, memories_embeddings, memories_weights)
        loss = self.criterion(logits, labels) if labels is not None else None
        return SequenceClassifierOutput(loss=loss, logits=logits)

    def _estimate_confidence(
        self,
        attention_weights: list[float] | NDArray[np.float32],
        memory_scores: list[float] | NDArray[np.float32],
    ) -> float:
        """
        Estimate the confidence of a regression prediction based on attention weights and memory scores.

        The confidence is computed using:
        1. Attention entropy: How focused vs spread out the attention is
        2. Score variance: How much the scores of attended memories vary

        Args:
            attention_weights: The attention weights for each memory
            memory_scores: The scores of each memory

        Returns:
            A confidence score between 0 and 1
        """
        from scipy.stats import entropy

        # Convert to numpy arrays if needed
        attention_weights = np.array(attention_weights, dtype=np.float32)
        memory_scores = np.array(memory_scores, dtype=np.float32)

        # Normalize attention weights to sum to 1
        attention_weights = attention_weights / np.sum(attention_weights)

        # Compute attention entropy (normalized to [0, 1])
        max_entropy = np.log(len(attention_weights))
        attention_entropy = entropy(attention_weights) / max_entropy if max_entropy > 0 else 0
        attention_focus = 1 - attention_entropy  # Higher focus = more confident

        # Compute weighted standard deviation of scores
        weighted_mean = np.sum(attention_weights * memory_scores)
        weighted_var = np.sum(attention_weights * (memory_scores - weighted_mean) ** 2)
        weighted_std = np.sqrt(weighted_var)

        # Scale std to [0, 1] using a soft threshold
        # We use 2 * weighted_mean as a reference - if std is larger than this, confidence goes to 0
        score_consistency = 1 / (1 + (weighted_std / (abs(weighted_mean) + 1e-6)))

        # Combine the two factors with more weight on score consistency
        confidence = 0.3 * attention_focus + 0.7 * score_consistency

        return float(confidence)

    @overload
    def predict(self, value: InputType, use_lookup_cache: bool = True) -> ScorePredictionWithMemories:
        pass

    @overload
    def predict(self, value: InputTypeList, use_lookup_cache: bool = True) -> list[ScorePredictionWithMemories]:
        pass

    @torch.no_grad()
    def predict(
        self, value: InputType | InputTypeList, use_lookup_cache: bool = True
    ) -> ScorePredictionWithMemories | list[ScorePredictionWithMemories]:
        """
        Predict the score for a given input

        Args:
            value: The input to predict the score for
            use_lookup_cache: Whether to use the lookup cache

        Returns:
            Either a single prediction or a list of predictions depending on the input type
        """
        timestamp = datetime.now(timezone.utc)

        lookup_res = cast(
            "ScoredMemoryLookupColumnResult",
            self.memoryset.lookup(
                [value] if not isinstance(value, list) else value,
                count=self.memory_lookup_count,
                return_type="columns",
                use_cache=use_lookup_cache,
            ),
        )
        logits = self.forward(
            input_embeddings=torch.tensor(lookup_res["input_embeddings"]).to(self.device),
            memories_scores=torch.tensor(lookup_res["memories_scores"]).to(self.device),
            memories_embeddings=torch.tensor(lookup_res["memories_embeddings"]).to(self.device),
            memories_weights=torch.tensor(lookup_res["memories_lookup_scores"]).to(self.device),
        ).logits
        predictions = logits

        results: list[ScorePredictionWithMemories] = []
        for i, prediction in enumerate(predictions):
            assert self.head.last_memories_attention_weights is not None
            prediction_id = uuid4()
            predicted_score = float(prediction.item())
            attention_weights = self.head.last_memories_attention_weights.tolist()[i]
            memory_scores = lookup_res["memories_scores"][i]

            confidence = self._estimate_confidence(attention_weights, memory_scores)
            anomaly_score = _estimate_anomaly_score(lookup_res, i)

            result_memory_lookups = [
                ScorePredictionMemoryLookup(
                    prediction_id=prediction_id,
                    value=lookup_res["memories_values"][i][j],
                    embedding=lookup_res["memories_embeddings"][i][j],
                    score=lookup_res["memories_scores"][i][j],
                    memory_id=lookup_res["memories_ids"][i][j],
                    memory_version=lookup_res["memories_versions"][i][j],
                    source_id=lookup_res["memories_source_ids"][i][j],
                    metadata=lookup_res["memories_metadata"][i][j],
                    metrics=None,
                    created_at=lookup_res["memories_created_ats"][i][j],
                    updated_at=lookup_res["memories_updated_ats"][i][j],
                    lookup_score=lookup_res["memories_lookup_scores"][i][j],
                    reranker_score=(
                        lookup_res["memories_reranker_scores"][i][j] if lookup_res["memories_reranker_scores"] else None
                    ),
                    reranker_embedding=(
                        lookup_res["memories_reranker_embeddings"][i][j]
                        if lookup_res["memories_reranker_embeddings"]
                        else None
                    ),
                    attention_weight=attention_weights[j],
                )
                for j in range(self.memory_lookup_count)
            ]
            result = ScorePredictionWithMemories(
                prediction_id=prediction_id,
                score=predicted_score,
                confidence=confidence,
                timestamp=timestamp,
                input_value=value[i] if isinstance(value, list) else value,
                input_embedding=lookup_res["input_embeddings"][i],
                logits=logits.to("cpu").numpy()[i],
                expected_score=None,
                memories=result_memory_lookups,
                anomaly_score=anomaly_score,
            )
            results.append(result)

        if not isinstance(value, list):
            return results[0]
        return results

    def evaluate(
        self,
        dataset: Dataset,
        value_column: str = "value",
        score_column: str = "score",
        batch_size: int = 32,
        on_progress: OnProgressCallback | None = None,
        on_predict: Callable[[list[ScorePredictionWithMemories]], None] | None = None,
    ) -> RegressionEvaluationResult:
        """
        Evaluate the model on a given dataset

        Args:
            dataset: The data to evaluate the model on
            value_column: The column in the dataset that contains the input values
            score_column: The column in the dataset that contains the expected scores
            batch_size: The batch size to use for evaluation
            on_progress: Optional callback to report progress
            on_predict: Optional callback to save telemetry for a batch of predictions

        Returns:
            The evaluation result with regression metrics
        """
        dataset = parse_dataset(dataset, value_column=value_column, score_column=score_column)

        # Track total loss and predictions for computing metrics
        total_loss = 0.0
        all_predictions: list[float] = []
        all_targets: list[float] = []
        total_samples = 0

        # Process dataset in batches
        if on_progress is not None:
            on_progress(0, len(dataset))
        for i in trange(0, len(dataset), batch_size, disable=on_progress is not None):
            batch = dataset[i : i + batch_size]
            batch_size_actual = len(batch["value"])

            # Get predictions for batch
            predictions = self.predict(batch["value"], use_lookup_cache=True)
            if not isinstance(predictions, list):
                predictions = [predictions]

            # Extract scores and targets
            batch_predictions = [p.score for p in predictions]
            batch_targets = batch["score"]

            # Compute loss for batch
            batch_loss = self.criterion(
                torch.tensor(batch_predictions, device=self.device),
                torch.tensor(batch_targets, device=self.device),
            ).item()

            # Accumulate results
            total_loss += batch_loss * batch_size_actual
            all_predictions.extend(batch_predictions)
            all_targets.extend(batch_targets)
            total_samples += batch_size_actual

            if on_progress:
                on_progress(total_samples, len(dataset))

            if on_predict:
                # Set expected scores for the entire batch
                for j, prediction in enumerate(predictions):
                    prediction.expected_score = batch["score"][j]
                on_predict(predictions)

        # Convert to numpy arrays for metric computation
        predictions_array = np.array(all_predictions)
        targets_array = np.array(all_targets)

        # Compute MSE and RMSE
        mse = float(mean_squared_error(targets_array, predictions_array))
        rmse = float(np.sqrt(mse))

        # Compute other metrics
        mae = float(mean_absolute_error(targets_array, predictions_array))
        r2 = float(r2_score(targets_array, predictions_array))
        explained_var = float(explained_variance_score(targets_array, predictions_array))

        return RegressionEvaluationResult(
            mse=mse,
            rmse=rmse,
            mae=mae,
            r2=r2,
            explained_variance=explained_var,
            loss=total_loss / total_samples,
        )


class RACModelConfig(PretrainedConfig):
    model_type = "rac-model"

    head_type: RACHeadType
    num_classes: int | None
    memoryset_uri: str | None
    memory_lookup_count: int | None
    weigh_memories: bool | None
    min_memory_weight: float | None
    num_layers: int | None
    dropout_prob: float | None

    def __init__(
        self,
        memoryset_uri: str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool | None = None,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
        **kwargs,
    ):
        """
        Initialize the config

        Note:
            While all args of a pretrained config must be optional, `memoryset_uri` must be specified.

        Args:
            memoryset_uri: URI of the memoryset to use, this is required
            memory_lookup_count: Number of memories to lookup for each input,
                by default the system uses a simple heuristic to choose a number of memories that works well in most cases
            head_type: Type of classification head to use
            num_classes: Number of classes to predict, will be inferred from memoryset if not specified
            weigh_memories: Optional parameter for KNN head, whether to weigh memories by their lookup score
            min_memory_weight: Optional parameter for KNN head, minimum memory weight under which memories are ignored
            num_layers: Optional parameter for FF head, number of layers in the feed forward network
            dropout_prob: Optional parameter for FF head, dropout probability
        """
        # We cannot require memoryset_uri here, because this class must be initializable without
        # passing any parameters for the PretrainedConfig.save_pretrained method to work, so instead
        # we throw an error in the RetrievalAugmentedClassifier initializer if it is missing
        self.memoryset_uri = memoryset_uri
        self.memory_lookup_count = memory_lookup_count
        self.head_type = head_type if isinstance(head_type, RACHeadType) else RACHeadType(head_type)
        self.num_classes = num_classes
        self.weigh_memories = weigh_memories
        self.min_memory_weight = min_memory_weight
        self.num_layers = num_layers
        self.dropout_prob = dropout_prob
        super().__init__(**kwargs)


class RACModel(PreTrainedModel):
    config_class = RACModelConfig
    base_model_prefix = "rac"
    memory_lookup_count: int

    def _init_head(self):
        # TODO: break this up into three subclasses that inherit from RACModel and have their own con
        match self.config.head_type:
            case RACHeadType.MMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = MemoryMixtureOfExpertsClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                )
            case RACHeadType.BMMOE:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = BalancedMemoryMixtureOfExpertsClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                )
            case RACHeadType.KNN:
                self.memory_lookup_count = self.config.memory_lookup_count or min(round(self.num_classes * 1.5) * 3, 50)
                self.head = NearestMemoriesClassificationHead(
                    num_classes=self.num_classes,
                    weigh_memories=self.config.weigh_memories,
                    min_memory_weight=self.config.min_memory_weight,
                )
            case RACHeadType.FF:
                self.memory_lookup_count = 0
                self.head = FeedForwardClassificationHead(
                    num_classes=self.num_classes,
                    embedding_dim=self.embedding_dim,
                    num_layers=self.config.num_layers,
                )
            case _:
                raise ValueError(f"Unsupported head type: {self.config.head_type}")

    @overload
    def __init__(self, config: RACModelConfig):
        pass

    @overload
    def __init__(
        self,
        *,
        memoryset: LabeledMemoryset | str,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        pass

    def __init__(
        self,
        config: RACModelConfig | None = None,
        *,
        memoryset: LabeledMemoryset | str | None = None,
        memory_lookup_count: int | None = None,
        head_type: RACHeadType | Literal["MMOE", "BMMOE", "KNN", "FF"] = RACHeadType.MMOE,
        num_classes: int | None = None,
        weigh_memories: bool = False,
        min_memory_weight: float | None = None,
        num_layers: int | None = None,
        dropout_prob: float | None = None,
    ):
        if config is None:
            assert memoryset is not None
            if isinstance(memoryset, LabeledMemoryset):
                self.memoryset = memoryset
            else:
                self.memoryset = LabeledMemoryset.connect(memoryset)
            config = RACModelConfig(
                memoryset_uri=self.memoryset.uri,
                memory_lookup_count=memory_lookup_count,
                head_type=head_type,
                num_classes=num_classes,
                weigh_memories=weigh_memories,
                min_memory_weight=min_memory_weight,
                num_layers=num_layers,
                dropout_prob=dropout_prob,
            )
        else:
            assert (
                memoryset is not None
                or memory_lookup_count is not None
                or head_type is not None
                or num_classes is not None
                or weigh_memories is not None
                or min_memory_weight is not None
                or num_layers is not None
                or dropout_prob is not None
            ), "Either config or kwargs can be provided, not both"
            if not config.memoryset_uri:
                # all configs must have defaults in a PretrainedConfig, but this one is required
                raise ValueError("memoryset_uri must be specified in config")
            self.memoryset = LabeledMemoryset.connect(config.memoryset_uri)
        super().__init__(config)
        self.embedding_dim = self.memoryset.embedding_model.embedding_dim
        if config.num_classes is None:
            logging.warning("num_classes not specified in config, using number of classes in memoryset")
            self.num_classes = self.memoryset.num_classes
        else:
            self.num_classes = config.num_classes
        self._init_head()
        self.criterion = nn.CrossEntropyLoss() if config.num_labels > 1 else nn.MSELoss()

    @property
    def num_trainable_parameters(self) -> int:
        """Number of trainable parameters in the model"""
        return self.num_parameters(only_trainable=True)

    def reset(self):
        """
        Reset the model weights to their initial state
        """
        self._init_head()

    def attach(self, memoryset: LabeledMemoryset | str):
        """
        Attach a memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset
        """
        self.memoryset = memoryset if isinstance(memoryset, LabeledMemoryset) else LabeledMemoryset.connect(memoryset)

    def use(self, memoryset: LabeledMemoryset | str):
        """
        Temporarily attach a different memoryset to the model

        Args:
            memoryset: The memoryset to attach to the model or a URI to a memoryset

        Examples:
            with model.use(memoryset):
                model.predict("test input")
        """

        @contextmanager
        def ctx_manager():
            previous_memoryset = self.memoryset
            try:
                self.attach(memoryset)
                yield
            finally:
                if previous_memoryset:
                    self.attach(previous_memoryset)

        return ctx_manager()

    def forward(
        self,
        input_embeddings: Tensor | None = None,
        memories_labels: Tensor | None = None,
        memories_embeddings: Tensor | None = None,
        memories_weights: Tensor | None = None,
        labels: Tensor | None = None,
    ) -> SequenceClassifierOutput:
        logits = self.head(input_embeddings, memories_labels, memories_embeddings, memories_weights)
        loss = self.criterion(logits, labels) if labels is not None else None
        return SequenceClassifierOutput(loss=loss, logits=logits)

    def finetune(
        self,
        checkpoint_dir: str | None = None,
        train_dataset: Dataset | None = None,
        eval_dataset: Dataset | None = None,
        value_column: str = "value",
        label_column: str = "label",
        training_args: RACTrainingArguments = RACTrainingArguments(),
        on_progress: OnProgressCallback | None = None,
        on_log: OnLogCallback | None = None,
    ):
        """
        Finetune the model on a given dataset

        Args:
            checkpoint_dir: The directory to save the checkpoint to, if this is `None` no checkpoint will be saved
            train_dataset: The data to finetune on, if this is `None` the memoryset will be used
            eval_dataset: The data to evaluate the finetuned model on, if this is `None` no evaluations will be performed
            value_column: The column in the dataset that contains the input values
            label_column: The column in the dataset that contains the expected labels
            training_args: The training arguments to use for the finetuning
            on_progress: Callback to report progress
        """
        if not train_dataset:
            train_dataset = self.memoryset.to_dataset()
        else:
            train_dataset = parse_dataset(train_dataset, value_column=value_column, label_column=label_column)
        if eval_dataset:
            eval_dataset = parse_dataset(eval_dataset, value_column=value_column, label_column=label_column)

        finetune(
            self,
            checkpoint_dir=checkpoint_dir,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            training_args=training_args,
            on_progress=on_progress,
            on_log=on_log,
        )

    def evaluate(
        self,
        dataset: Dataset,
        value_column: str = "value",
        label_column: str = "label",
        batch_size: int = 32,
        on_progress: OnProgressCallback | None = None,
        on_predict: Callable[[list[LabelPredictionWithMemories]], None] | None = None,
    ) -> ClassificationEvaluationResult:
        """
        Evaluate the model on a given dataset

        Args:
            dataset: The data to evaluate the model on
            value_column: The column in the dataset that contains the input values
            label_column: The column in the dataset that contains the expected labels
            batch_size: The batch size to use for evaluation
            on_progress: Optional callback to report progress
            on_predict: Optional callback to save telemetry for a batch of predictions

        Returns:
            The evaluation result
        """
        dataset = parse_dataset(dataset, value_column=value_column, label_column=label_column)

        # Track total loss and predictions for computing metrics
        total_loss = 0.0
        all_predictions: list[int] = []
        all_targets: list[int] = []
        all_logits: list[Tensor] = []
        total_samples = 0

        # Process dataset in batches
        if on_progress is not None:
            on_progress(0, len(dataset))
        for i in trange(0, len(dataset), batch_size, disable=on_progress is not None):
            batch = dataset[i : i + batch_size]
            batch_size_actual = len(batch["value"])

            # Get predictions for batch
            predictions = self.predict(batch["value"], use_lookup_cache=True)
            if not isinstance(predictions, list):
                predictions = [predictions]

            # Process predictions if callback provided
            if on_predict:
                # Set expected labels for the entire batch
                for j, prediction in enumerate(predictions):
                    prediction.expected_label = batch["label"][j]
                on_predict(predictions)

            # Extract predictions and targets
            batch_logits = torch.tensor(np.array([p.logits for p in predictions]), device=self.device)
            batch_targets = torch.tensor(batch["label"], device=self.device)

            # Compute loss for batch using logits
            batch_loss = self.criterion(batch_logits, batch_targets).item()

            # Get predicted labels from logits for metrics
            batch_predictions = [p.label for p in predictions]

            # Accumulate results
            total_loss += batch_loss * batch_size_actual
            all_predictions.extend(batch_predictions)
            all_logits.extend(batch_logits)
            all_targets.extend(batch["label"])
            total_samples += batch_size_actual

            if on_progress:
                on_progress(total_samples, len(dataset))

        # Convert to numpy arrays for metric computation
        predictions_array = np.array(all_predictions)
        targets_array = np.array(all_targets)
        logits_array = torch.stack(all_logits).cpu().numpy()

        return ClassificationEvaluationResult.calculate_metrics(
            logits_array=logits_array,
            targets_array=targets_array,
            predictions_array=predictions_array,
            total_loss=total_loss,
        )

    @overload
    def predict(self, value: InputType, use_lookup_cache: bool = True) -> LabelPredictionWithMemories:
        pass

    @overload
    def predict(self, value: InputTypeList, use_lookup_cache: bool = True) -> list[LabelPredictionWithMemories]:
        pass

    @torch.no_grad()
    def predict(
        self, value: InputType | InputTypeList, use_lookup_cache: bool = True
    ) -> LabelPredictionWithMemories | list[LabelPredictionWithMemories]:
        """
        Predict the label for a given input

        Args:
            value: The input to predict the label for
            use_lookup_cache: Whether to use the lookup cache

        Returns:
            Either a single prediction or a list of predictions depending on the input type
        """
        timestamp = datetime.now(timezone.utc)

        lookup_res = self.memoryset.lookup(
            [value] if not isinstance(value, list) else value,
            count=self.memory_lookup_count,
            return_type="columns",
            use_cache=use_lookup_cache,
        )
        logits = self.forward(
            input_embeddings=torch.tensor(lookup_res["input_embeddings"]).to(self.device),
            memories_labels=torch.tensor(lookup_res["memories_labels"]).to(self.device),
            memories_embeddings=torch.tensor(lookup_res["memories_embeddings"]).to(self.device),
            memories_weights=torch.tensor(lookup_res["memories_lookup_scores"]).to(self.device),
        ).logits
        label_predictions = torch.argmax(logits, dim=-1)

        results: list[LabelPredictionWithMemories] = []
        for i, prediction in enumerate(label_predictions):
            prediction_id = uuid4()
            predicted_label = int(prediction.item())
            anomaly_score = _estimate_anomaly_score(lookup_res, i)
            result_memory_lookups = [
                LabelPredictionMemoryLookup(
                    prediction_id=prediction_id,
                    value=lookup_res["memories_values"][i][j],
                    embedding=lookup_res["memories_embeddings"][i][j],
                    label=lookup_res["memories_labels"][i][j],
                    label_name=lookup_res["memories_label_names"][i][j],
                    memory_id=lookup_res["memories_ids"][i][j],
                    memory_version=lookup_res["memories_versions"][i][j],
                    source_id=lookup_res["memories_source_ids"][i][j],
                    metadata=lookup_res["memories_metadata"][i][j],
                    metrics=None,
                    created_at=lookup_res["memories_created_ats"][i][j],
                    updated_at=lookup_res["memories_updated_ats"][i][j],
                    lookup_score=lookup_res["memories_lookup_scores"][i][j],
                    reranker_score=(
                        lookup_res["memories_reranker_scores"][i][j] if lookup_res["memories_reranker_scores"] else None
                    ),
                    reranker_embedding=(
                        lookup_res["memories_reranker_embeddings"][i][j]
                        if lookup_res["memories_reranker_embeddings"]
                        else None
                    ),
                    # does not run for feed forward heads since they use memory_lookup_count = 0
                    attention_weight=cast(Tensor, self.head.last_memories_attention_weights).tolist()[i][j],
                )
                for j in range(self.memory_lookup_count)
            ]
            result = LabelPredictionWithMemories(
                prediction_id=prediction_id,
                label=predicted_label,
                label_name=self.memoryset.get_label_name(predicted_label),
                expected_label=None,
                confidence=float(logits[i][predicted_label].item()),
                timestamp=timestamp,
                input_value=value[i] if isinstance(value, list) else value,
                input_embedding=lookup_res["input_embeddings"][i],
                logits=logits.to("cpu").numpy()[i],
                memories=result_memory_lookups,
                anomaly_score=anomaly_score,
            )
            results.append(result)

        if not isinstance(value, list):
            return results[0]
        return results

    def save_pretrained(self, save_directory: str, **kwargs):  # type: ignore
        """
        Save the model to a local or remote directory

        Args:
            save_directory: The directory to save the model to

        Examples:
            model.save_pretrained("./temp/my-model)
            model.save_pretrained("gs:/orca-internal/models/my-model")
        """
        if not is_using_blob_storage(save_directory):
            return super().save_pretrained(save_directory, **kwargs)
        # if we want to save to blob storage, we need to save to a temporary directory first
        with TemporaryDirectory() as temp_dir:
            super().save_pretrained(temp_dir, **kwargs)
            upload_dir(temp_dir, save_directory, recursive=False)

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path: str) -> RACModel:
        """
        Load the model from a local or remote directory

        Args:
            pretrained_model_name_or_path: The directory to load the model from

        Returns:
            The loaded model

        Examples:
            model = RACModel.from_pretrained("./temp/my-model")
            model = RACModel.from_pretrained("gs:/orca-internal/models/my-model")
        """
        if not is_using_blob_storage(pretrained_model_name_or_path):
            return cast(RACModel, super().from_pretrained(pretrained_model_name_or_path))
        # if the model is in blob storage, download it to a temporary directory first
        with TemporaryDirectory() as temp_dir:
            download_dir(pretrained_model_name_or_path, temp_dir, recursive=False)
            return cast(RACModel, super().from_pretrained(temp_dir))


AutoConfig.register("rac-model", RACModelConfig)
AutoModelForSequenceClassification.register(RACModelConfig, RACModel)
AutoModelForImageClassification.register(RACModelConfig, RACModel)

import math
import os
from datetime import datetime
from uuid import UUID

import numpy as np
import torch

from ..fs_utils import is_using_blob_storage, list_dir
from .model import (
    ClassificationEvaluationResult,
    LabeledMemoryLookup,
    LabelPredictionWithMemories,
    MemoryMixtureOfExpertsClassificationHead,
    MemoryMixtureOfExpertsRegressionHead,
    NearestMemoriesClassificationHead,
    RACModel,
    RACTrainingArguments,
    RARModel,
    RegressionEvaluationResult,
    ScorePredictionWithMemories,
)


def test_initialize_model(memoryset):
    # When a model is initialized with a memoryset
    model = RACModel(memoryset=memoryset, head_type="MMOE")
    # Then the model is initialized without errors
    assert model is not None
    # And the memoryset is attached to the model
    assert model.memoryset is memoryset
    # And it has the correct head
    assert isinstance(model.head, MemoryMixtureOfExpertsClassificationHead)
    # And a reasonable memory lookup count is inferred
    assert model.memory_lookup_count == 9
    # And the number of classes is inferred from the memoryset
    assert model.num_classes == 2
    # And the forward method returns a valid output
    batch_size = 2
    memories_labels = torch.tensor([[1] * 9, [0] * 9])
    assert memories_labels.shape == (batch_size, model.memory_lookup_count)
    input_embeddings = torch.rand(batch_size, model.memoryset.embedding_model.embedding_dim)
    memories_embeddings = torch.rand(
        batch_size, model.memory_lookup_count, model.memoryset.embedding_model.embedding_dim
    )
    expected_labels = torch.tensor([1, 0])
    assert expected_labels.shape == (batch_size,)
    output = model(
        input_embeddings=input_embeddings,
        memories_labels=memories_labels,
        memories_embeddings=memories_embeddings,
        memories_weights=None,
        labels=expected_labels,
    )
    assert output is not None
    assert output.loss is not None
    assert output.logits is not None
    assert output.logits.shape == (batch_size, model.num_classes)
    assert (output.logits.argmax(dim=-1) == expected_labels).all()


def test_save_and_load_model(location, memoryset):
    # Given a RAC model
    model = RACModel(memoryset=memoryset, head_type="KNN", weigh_memories=True)
    # When the model is saved
    model.save_pretrained(location)
    # Then the remote bucket should contain the model files
    if is_using_blob_storage(location):
        model_files = list_dir(location)
        assert len(model_files) > 0
        assert f"{location}/config.json" in model_files
    else:
        model_files = os.listdir(location)
        assert len(model_files) > 0
        assert "config.json" in model_files
    # When the model is loaded back up
    reloaded_model = RACModel.from_pretrained(location)
    # Then the model is loaded without errors
    assert reloaded_model is not None
    # And the memoryset is correctly attached
    assert reloaded_model.memoryset.uri == memoryset.uri
    assert len(reloaded_model.memoryset) == len(memoryset)
    # And the config is loaded correctly
    assert isinstance(reloaded_model.head, NearestMemoriesClassificationHead)
    assert reloaded_model.config.weigh_memories is True


def test_evaluate(memoryset, dataset_dict):
    # Given a RAC model
    model = RACModel(memoryset=memoryset, head_type="KNN", min_memory_weight=0.5)
    # And a progress callback
    progress_calls = []
    progress_callback = lambda step, total: progress_calls.append((step, total))  # noqa: E731
    # When the model is evaluated
    result = model.evaluate(
        dataset_dict["test"].rename_column("label", "category"),
        value_column="text",
        label_column="category",
        on_progress=progress_callback,
        batch_size=len(dataset_dict["test"]) // 2,
    )

    # Then a result is returned
    assert isinstance(result, ClassificationEvaluationResult)
    # And the result contains all the metrics
    assert result.accuracy > 0.7
    assert result.f1_score > 0.7
    assert isinstance(result.loss, float)
    assert result.roc_curve is not None
    assert result.precision_recall_curve is not None
    assert result.roc_curve.auc > 0.7
    assert result.precision_recall_curve.auc > 0.7

    assert len(result.precision_recall_curve.precisions) == len(result.precision_recall_curve.recalls)
    assert len(result.precision_recall_curve.precisions) == len(result.precision_recall_curve.thresholds)
    assert len(result.roc_curve.false_positive_rates) == len(result.roc_curve.true_positive_rates)
    assert len(result.roc_curve.false_positive_rates) == len(result.roc_curve.thresholds)

    # And the progress callback is called
    assert len(progress_calls) == 3
    assert progress_calls[0] == (0, len(dataset_dict["test"]))
    assert progress_calls[1] == (len(dataset_dict["test"]) // 2, len(dataset_dict["test"]))
    assert progress_calls[2] == (len(dataset_dict["test"]), len(dataset_dict["test"]))


def test_finetune(location_or_none, memoryset, dataset_dict):
    # Given a RAC model
    model = RACModel(memoryset=memoryset, head_type="FF")
    # And a progress callback
    progress_calls = []
    progress_callback = lambda step, total: progress_calls.append((step, total))  # noqa: E731
    # And a log callback
    logs = []
    log_callback = lambda log: logs.append(log)  # noqa: E731
    # When the model is finetuned
    pre_finetune_metrics = model.evaluate(dataset_dict["train"], value_column="text")
    model.finetune(
        location_or_none,
        train_dataset=dataset_dict["train"],
        eval_dataset=dataset_dict["test"],
        value_column="text",
        on_log=log_callback,
        training_args=RACTrainingArguments(
            max_steps=4,
            warmup_steps=0,
            eval_strategy="steps",
            eval_steps=4,
            logging_steps=1,
            per_device_train_batch_size=16,
        ),
        on_progress=progress_callback,
    )
    # Then the model is fit to the training data
    post_finetune_metrics = model.evaluate(dataset_dict["train"], value_column="text")
    assert post_finetune_metrics.loss < pre_finetune_metrics.loss
    assert post_finetune_metrics.accuracy > pre_finetune_metrics.accuracy
    # And the progress callback is called
    assert len(progress_calls) == 4 + 1
    for i in range(4 + 1):
        assert progress_calls[i] == (i, 4)
    # And the log callback is called
    assert len(logs) >= 4
    for log in logs[:4]:
        assert "epoch" in log
        assert isinstance(log["epoch"], float)
        assert "loss" in log
        assert isinstance(log["loss"], float)
        assert "grad_norm" in log
        assert isinstance(log["grad_norm"], float)
        assert "learning_rate" in log
        assert isinstance(log["learning_rate"], float)
    # And training checkpoints are saved
    if location_or_none is not None:
        files_at_location = list_dir(location_or_none)
        assert len(files_at_location) > 0
        assert any("checkpoint" in f for f in files_at_location)


def test_predict(memoryset, dataset_dict, label_names):
    # Given a RAC model
    model = RACModel(memoryset=memoryset)
    # When predict is called with a single text
    prediction = model.predict(dataset_dict["test"]["text"][0])
    # Then a single prediction is returned
    assert prediction is not None
    assert isinstance(prediction, LabelPredictionWithMemories)
    # And the prediction contains a label
    assert prediction.label in [0, 1]
    # And the label name is resolved
    assert prediction.label_name in label_names
    # And the prediction contains a confidence
    assert 0 <= prediction.confidence <= 1
    # And the prediction contains an anomaly score
    assert prediction.anomaly_score is not None
    # And the logits are a numpy array
    assert isinstance(prediction.logits, np.ndarray)
    assert prediction.logits.shape == (model.num_classes,)
    assert prediction.logits.dtype == np.float32
    # And the input embedding is a numpy array
    assert isinstance(prediction.input_embedding, np.ndarray)
    assert prediction.input_embedding.shape == (model.memoryset.embedding_model.embedding_dim,)
    assert prediction.input_embedding.dtype == np.float32
    # And a prediction id is returned
    prediction_id = prediction.prediction_id
    assert isinstance(prediction_id, UUID)
    # And a timestamp is returned
    assert isinstance(prediction.timestamp, datetime)
    # And the memory lookups
    assert isinstance(prediction.memories, list)
    assert len(prediction.memories) == model.memory_lookup_count
    assert isinstance(prediction.memories[0], LabeledMemoryLookup)
    # And the memory lookups contain the attention weights
    assert prediction.memories[0].attention_weight is not None
    assert isinstance(prediction.memories[0].attention_weight, float)
    # And the memory lookups contain the prediction id
    assert prediction.memories[0].prediction_id == prediction_id


def test_predict_batch(memoryset, dataset_dict):
    # Given a RAC model
    model = RACModel(memoryset=memoryset)
    # When predict is called with a batch of texts
    predictions = model.predict(dataset_dict["test"]["text"][:2])
    # Then a list of predictions is returned
    assert isinstance(predictions, list)
    assert len(predictions) == 2
    # And each prediction is of the correct type
    assert all(isinstance(prediction, LabelPredictionWithMemories) for prediction in predictions)
    # And the prediction results contain memories
    assert all(isinstance(prediction.memories[0], LabeledMemoryLookup) for prediction in predictions)


def test_initialize_rar_model(scored_memoryset):
    # When a model is initialized with a memoryset
    model = RARModel(memoryset=scored_memoryset, head_type="mmoe")
    # Then the model is initialized without errors
    assert model is not None
    # And the memoryset is attached to the model
    assert model.memoryset is scored_memoryset
    # And it has the correct head
    assert isinstance(model.head, MemoryMixtureOfExpertsRegressionHead)
    # And a reasonable memory lookup count is set
    assert model.memory_lookup_count == 10
    # And the forward method returns a valid output
    batch_size = 2
    memories_scores = torch.tensor([[0.5] * 10, [0.8] * 10])
    assert memories_scores.shape == (batch_size, model.memory_lookup_count)
    input_embeddings = torch.rand(batch_size, model.memoryset.embedding_model.embedding_dim)
    memories_embeddings = torch.rand(
        batch_size, model.memory_lookup_count, model.memoryset.embedding_model.embedding_dim
    )
    expected_scores = torch.tensor([0.6, 0.7])
    assert expected_scores.shape == (batch_size,)
    output = model(
        input_embeddings=input_embeddings,
        memories_scores=memories_scores,
        memories_embeddings=memories_embeddings,
        memories_weights=None,
        labels=expected_scores,
    )
    assert output is not None
    assert output.loss is not None
    assert output.logits is not None
    assert output.logits.shape == (batch_size,)  # Single score output


def test_evaluate_rar_model(scored_memoryset, scored_dataset_dict):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset, head_type="mmoe")
    # And a progress callback
    progress_calls = []
    progress_callback = lambda step, total: progress_calls.append((step, total))  # noqa: E731
    # When the model is evaluated
    result = model.evaluate(
        scored_dataset_dict["test"].rename_column("score", "label"),
        value_column="text",
        score_column="label",
        on_progress=progress_callback,
        batch_size=len(scored_dataset_dict["test"]) // 2,
    )
    # Then a result is returned
    assert isinstance(result, RegressionEvaluationResult)
    # And the result contains all the metrics
    assert result.mse >= 0  # MSE is always non-negative
    assert result.rmse >= 0  # RMSE is always non-negative
    assert result.mae >= 0  # MAE is always non-negative
    assert isinstance(result.r2, float)  # R2 can be negative for poor fits
    assert isinstance(result.explained_variance, float)
    assert isinstance(result.loss, float)
    # And the progress callback is called
    assert len(progress_calls) == 3
    assert progress_calls[0] == (0, len(scored_dataset_dict["test"]))
    assert progress_calls[1] == (len(scored_dataset_dict["test"]) // 2, len(scored_dataset_dict["test"]))
    assert progress_calls[2] == (len(scored_dataset_dict["test"]), len(scored_dataset_dict["test"]))


def test_predict_rar_model(scored_memoryset, scored_dataset_dict):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset)
    # When predict is called with a single text
    prediction = model.predict(scored_dataset_dict["test"]["text"][0])
    # Then a single prediction is returned
    assert prediction is not None
    assert isinstance(prediction, ScorePredictionWithMemories)
    # And the prediction contains a score
    assert isinstance(prediction.score, float)
    # And the prediction contains a confidence
    assert 0 <= prediction.confidence <= 1
    # And the prediction contains an anomaly score
    assert prediction.anomaly_score is not None
    # And the logits are a numpy array
    assert isinstance(prediction.logits, float)
    # And the input embedding is a numpy array
    assert isinstance(prediction.input_embedding, np.ndarray)
    assert prediction.input_embedding.shape == (model.memoryset.embedding_model.embedding_dim,)
    assert prediction.input_embedding.dtype == np.float32
    # And a prediction id is returned
    prediction_id = prediction.prediction_id
    assert isinstance(prediction_id, UUID)
    # And a timestamp is returned
    assert isinstance(prediction.timestamp, datetime)
    # And the memory lookups
    assert isinstance(prediction.memories, list)
    assert len(prediction.memories) == model.memory_lookup_count
    # And the memory lookups contain the attention weights
    assert prediction.memories[0].attention_weight is not None
    assert isinstance(prediction.memories[0].attention_weight, float)
    # And the memory lookups contain the prediction id
    assert prediction.memories[0].prediction_id == prediction_id


def test_predict_batch_rar_model(scored_memoryset, scored_dataset_dict):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset)
    # When predict is called with a batch of texts
    predictions = model.predict(scored_dataset_dict["test"]["text"][:2])
    # Then a list of predictions is returned
    assert isinstance(predictions, list)
    assert len(predictions) == 2
    # And each prediction is of the correct type
    assert all(isinstance(prediction, ScorePredictionWithMemories) for prediction in predictions)
    # And each prediction has the correct number of memories
    assert all(len(prediction.memories) == model.memory_lookup_count for prediction in predictions)
    # And each prediction has valid scores and confidences
    assert all(isinstance(prediction.score, float) for prediction in predictions)
    assert all(0 <= prediction.confidence <= 1 for prediction in predictions)


def test_confidence_estimation_rar_model(scored_memoryset):
    # Given a RAR model
    model = RARModel(memoryset=scored_memoryset)

    # Test case 1: Focused attention on similar scores
    focused_weights = [0.8, 0.1, 0.1]
    similar_scores = [0.5, 0.51, 0.49]
    high_confidence = model._estimate_confidence(focused_weights, similar_scores)

    # Test case 2: Spread out attention on varied scores
    spread_weights = [0.4, 0.3, 0.3]
    varied_scores = [0.1, 0.5, 0.9]
    low_confidence = model._estimate_confidence(spread_weights, varied_scores)

    # Then the confidence should be higher for focused attention on similar scores
    assert high_confidence > low_confidence
    # And both confidences should be between 0 and 1
    assert 0 <= high_confidence <= 1
    assert 0 <= low_confidence <= 1

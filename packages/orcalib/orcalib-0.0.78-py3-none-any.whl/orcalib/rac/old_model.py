import logging
import sys
import uuid
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, replace
from statistics import mean
from typing import Callable, Type

import numpy as np
import torch
import torch.nn as nn
from safetensors import safe_open
from safetensors.torch import load_file, save_file
from tqdm.auto import tqdm
from typing_extensions import deprecated

from orcalib.memoryset import EmbeddingModel, InputType, InputTypeList, LabeledMemoryset
from orcalib.rac.old_model_util import DatasetLike, format_dataset

from .old_model_head_models import RACHeadInitConfig, RACHeadProtocol, SimpleMMOEHead
from .old_model_metrics import (
    AnalyzeResult,
    aggregate_memory_stats,
    analyze_result,
    compute_prediction_metrics,
)
from .old_return_types import EvalResult, LabeledMemoryLookupStats, PredictionResult
from .visualization import FinetunePlot, print_memories_table, visualize_explain


@dataclass(frozen=True)
class TrainingConfig:
    lr: float = 1e-4
    epochs: int = 1
    batch_size: int = 32
    gradient_accumulation_steps: int = 1


@deprecated("Use RACModel instead")
class OldRACModel(nn.Module):
    def __init__(
        self,
        num_classes: int,
        *,
        head: Type[RACHeadProtocol] = SimpleMMOEHead,
        num_memories: int | None = None,
        memoryset: LabeledMemoryset | None = None,
        embedding_model: EmbeddingModel | None = None,
        cross_encoder_model: str | None = None,
    ):
        # TODO: Support model run configuration like dtype and device (automagic with overrides)
        super().__init__()
        if num_memories is None:
            self.memory_lookup_count = min(round(num_classes * 1.5) * 5, 50)
        else:
            self.memory_lookup_count = num_memories

        self.memoryset = memoryset
        base_model = memoryset.embedding_model if memoryset else embedding_model
        if not base_model:
            raise ValueError("Embedding model was not provided and cannot be inferred from memoryset")
        self.base_model = base_model
        if not self.base_model.embedding_dim:
            raise ValueError("Embedding model must have a defined embedding dimension")
        # Set up the logger
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.head_class = head
        self.head_config = RACHeadInitConfig(
            embedding_dim=self.base_model.embedding_dim,
            num_classes=num_classes,
            cross_encoder_model=cross_encoder_model,
        )
        self.orca_model = self.head_class(self.head_config)
        if not isinstance(self.orca_model, nn.Module):
            raise ValueError("Head model must be an instance of nn.Module")

    def reset(self):
        """Reset model parameters to before they were trained"""
        self.orca_model = self.head_class(self.head_config)

    @property
    def num_parameters(self) -> int:
        """Number of trainable model parameters"""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def forward(
        self,
        input_embeddings: torch.Tensor,
        memory_embeddings: list[list[torch.Tensor]],
        memory_labels: list[list[int]],
        original_input: InputTypeList,
        original_memories: list[InputTypeList],
    ) -> torch.Tensor:
        assert isinstance(self.orca_model, nn.Module)
        return self.orca_model.forward(
            input_embeddings=torch.Tensor(input_embeddings),
            memory_embeddings=memory_embeddings,
            memory_labels=memory_labels,
            original_input=original_input,
            original_memories=original_memories,
        )

    def predict(
        self,
        inpt: InputType,
        expected_label: int | None = None,
        log: bool = False,
        curate: bool = False,
        feedback_callback: Callable[[int, int], float | int | bool] | None = None,
    ) -> PredictionResult:
        """
        Predicts the label for the given input.
        """
        return self.predict_batch(
            [inpt],
            [expected_label] if expected_label else None,
            log=log,
            curate=curate,
            feedback_callback=feedback_callback,
        )[0]

    def predict_batch(
        self,
        inputs: InputTypeList,
        expected_labels: list[int] | None = None,
        log: bool = False,
        curate: bool = True,
        feedback_callback: Callable[[int, int], float | int | bool] | None = None,
    ) -> list[PredictionResult]:
        # compute input embedding
        input_embeddings = self.base_model.embed(inputs, show_progress_bar=log)

        # lookup memories
        if self.orca_model.model_properties.needs_memories:
            if self.memoryset is None:
                raise ValueError("No memoryset attached to the model (use `attach` method)")

            if self.memoryset.embedding_model.name != self.base_model.name:
                raise ValueError(
                    f"Model mismatch between RAC and LabeledMemoryset: {self.base_model.name} != {self.memoryset.embedding_model.name}"
                )

            lookup_results = self.memoryset.lookup(input_embeddings, count=self.memory_lookup_count)

            memory_embeddings = [
                [torch.Tensor(memory.embedding) for memory in lookup_result] for lookup_result in lookup_results
            ]
            memory_labels = [[memory.label for memory in lookup_result] for lookup_result in lookup_results]
        else:
            # TODO: reconsider if using None might be better than using empty lists here
            lookup_results = []
            memory_embeddings = []
            memory_labels = []

        if self.orca_model.model_properties.needs_original_data:
            original_input = inputs
        else:
            original_input = []

        if self.orca_model.model_properties.needs_original_data and self.orca_model.model_properties.needs_memories:
            original_memories: list[InputTypeList] = [
                [memory.value for memory in lookup_result] for lookup_result in lookup_results
            ]
        else:
            original_memories = []

        logits = self.forward(
            input_embeddings=torch.Tensor(input_embeddings),
            memory_embeddings=memory_embeddings,
            memory_labels=memory_labels,
            original_input=original_input,
            original_memories=original_memories,
        )

        # build prediction results from the logits
        prediction_results = []
        for i, logit in enumerate(logits):
            prediction_results.append(
                PredictionResult(
                    label=int(torch.argmax(logit).item()),
                    label_name=None,  # TODO: add once available
                    confidence=torch.max(logit).item(),  # TODO: normalize this for easier interpretability
                    memories=(lookup_results[i] if self.orca_model.model_properties.needs_memories else []),
                    logits=logit.detach().to("cpu").numpy(),  # Detach the tensor before converting to numpy
                    input_embedding=input_embeddings[i],
                )
            )
        return prediction_results

    def attach(self, memoryset: LabeledMemoryset):
        # TODO(p2): support separate/different retrieval and predict models
        if memoryset.embedding_model.name != self.base_model.name:
            raise ValueError(
                f"Model mismatch between RAC and LabeledMemoryset: {self.base_model.name} != {memoryset.embedding_model.name}"
            )
        self.memoryset = memoryset

    def evaluate(
        self,
        dataset: DatasetLike | LabeledMemoryset,
        log: bool = False,
        batch_size: int = 64,
        curate: bool = True,
    ) -> EvalResult:
        """
        Benchmarks the model on the given dataset returning a bunch of different metrics.

        For dict-like or list of dict-like datasets, there must be a `label` key and one of the following keys: `text`, `image`, or `value`.
        If there are only two keys and one is `label`, the other will be inferred to be `value`.

        For list-like datasets, the first element of each tuple must be the value and the second must be the label.
        """
        if isinstance(dataset, LabeledMemoryset):
            dataset = dataset.to_list()
            # map through the dataset and convert it to a list of tuples with the keys `value` and `label`
            dataset = [(data.value, data.label) for data in dataset]
        # This enforces that all dataset have at least value and label columns
        formatted_dataset = format_dataset(dataset)

        self.logger.info("Evaluating model") if log else None

        examples = [data[0] for data in formatted_dataset]
        expected_labels = [data[1] for data in formatted_dataset]

        # run batch prediction with batch_size
        predictions: list[tuple[int, np.ndarray]] = []
        with torch.no_grad():
            for i in tqdm(range(0, len(formatted_dataset), batch_size), desc="Batch Predictions", disable=not log):
                predictions.extend(
                    [
                        (pred.label, pred.logits)
                        for pred in self.predict_batch(
                            examples[i : i + batch_size], expected_labels[i : i + batch_size], log=False, curate=curate
                        )
                    ]
                )

        self.logger.info("Computing Metrics") if log else None

        # Calculate metrics
        metrics = compute_prediction_metrics(predictions, expected_labels)
        return metrics

    def evaluate_and_explain(
        self,
        dataset: DatasetLike | LabeledMemoryset,
        log: bool = False,
        plot: bool = False,
        curate: bool = True,
    ) -> tuple[EvalResult, dict[str, LabeledMemoryLookupStats]]:
        """
        Benchmarks the model on the given dataset returning a bunch of different metrics.

        For dict-like or list of dict-like datasets, there must be a `label` key and one of the following keys: `text`, `image`, or `value`.
        If there are only two keys and one is `label`, the other will be inferred to be `value`.

        For list-like datasets, the first element of each tuple must be the value and the second must be the label.
        """

        if isinstance(dataset, LabeledMemoryset):
            dataset = dataset.to_list()
        formatted_dataset = format_dataset(dataset, log)

        # Batch create predictions from the formatted dataset
        self.logger.info("Evaluating model") if log else None

        predictions: list[PredictionResult] = []
        predictions = self.predict_batch(
            [data[0] for data in formatted_dataset], [data[1] for data in formatted_dataset], log=log, curate=curate
        )
        explanations = []
        for prediction in predictions:
            explanations.append(self.explain(prediction))

        # map through a list of stats and aggregate memory stats
        memory_stats = []
        label_stats = []
        for explanation in explanations:
            if explanation is not None:
                for memory_stat in explanation.memory_stats:
                    memory_stats.append(memory_stat)
                for label_stat in explanation.label_stats:
                    label_stats.append(label_stat)

        # Initialize dict to hold lists of scores by label
        memory_scores_by_label = defaultdict(lambda: {"lookup_scores": [], "attention_weights": []})

        for stat in memory_stats:
            # Check if stat is a dictionary and process accordingly
            if isinstance(stat, dict):
                label = stat.get("label")
                if label is not None:
                    memory_scores_by_label[label]["lookup_scores"].append(stat.get("lookup_score", 0))
                    memory_scores_by_label[label]["attention_weights"].append(stat.get("attention_weight", 0))

        # Function to calculate min, max, and median
        def calculate_stats(values):
            return {"min": min(values), "max": max(values), "median": np.median(values)}

        # Calculate stats for each label
        stats_by_label = {}
        for label, scores in memory_scores_by_label.items():
            stats_by_label[label] = {
                "count": len(scores["lookup_scores"]),
                "lookup_scores": calculate_stats(scores["lookup_scores"]),
                "attention_weights": calculate_stats(scores["attention_weights"]),
            }
        mem_stats = aggregate_memory_stats(predictions, formatted_dataset, plot)

        correct_labels = [data[1] for data in formatted_dataset]
        prediction_tuples = [(pred.label, pred.logits) for pred in predictions]
        self.logger.info("Computing Metrics") if log else None
        metrics = compute_prediction_metrics(prediction_tuples, correct_labels)
        self.logger.info("metrics: %s", metrics) if log else None
        return (metrics, mem_stats)

    def inspect_last_run(
        self,
    ):
        """Displays information about the memories accessed during the last run (incl weights etc.)"""
        raise NotImplementedError()

    def explain(
        self,
        prediction_result: PredictionResult | None = None,
        inpt: InputType | None = None,
        interactive: bool = False,
        plot: bool = False,
        pretty_print: bool = False,
    ) -> AnalyzeResult | None:
        """Like `predict` but instead of the prediction result, returns an explanation of the prediction (accessed memories etc.)

        :param inpt: The input to explain
        :param plot: If True, will display graphs via matplotlib
        :param pretty_print: If True, will return a pretty printed string of the explanation. If False, will return a dictionary
        :param interactive: DISABLED - ~~If True, will display the explanation in an interactive way (e.g. with a GUI)~~
        """
        if inpt is None and prediction_result is None:
            raise ValueError("Either result or inpt must be provided")
        if prediction_result is None and inpt is not None:
            result = self.predict(inpt, curate=False)
        else:
            result = prediction_result

        if result is None:
            raise ValueError("No result to analyze")
        analysis = analyze_result(result)
        visualize_explain(analysis) if plot else None
        if pretty_print:
            self.logger.info(print_memories_table(analysis))
        elif not plot:
            return analysis

    def finetune(
        self,
        dataset: DatasetLike,
        log: bool = False,
        config: TrainingConfig = TrainingConfig(),
        plot: bool = False,
        show_running_mean: bool = False,
        validation_dataset: DatasetLike | None = None,
        **kwargs,
    ):
        """Fine-tunes the model on a given dataset.

        :param dataset: The dataset to fine-tune on.
        :param log: If True, will log progress.
        :param config: Allows you to set learning rate, epochs, gradient accumulation steps, and batch size.
        :param plot: If True, will display a plot of the training progress.
        :param show_running_mean: If True, will display a running mean of the loss (trailing mean is default).
        :param validation_dataset: Exit tuning early once this dataset evaluation stops improving .
        """
        self.logger.info("Starting fine-tuning") if log else None
        assert isinstance(self.orca_model, nn.Module)
        # Generate a new UUID at the start of finetune
        current_finetune_uuid = str(uuid.uuid4())

        config = replace(config, **kwargs)

        # Initialize lists to store batch numbers and loss values
        fractional_epochs = []
        loss_values = []
        mean_loss_values = []
        total_loss_values = []
        batch_count = 0
        validation_scores = []
        stop_early = False

        if plot:
            plotter = FinetunePlot(show_running_mean=False)
            fig_widget = plotter.get_widget()
            if "ipykernel" in sys.modules:
                from IPython.display import display

                display(fig_widget)
        else:
            fig_widget = None
            plotter = None

        # Set up optimizer and loss function
        optimizer = torch.optim.Adam(self.orca_model.parameters(), lr=config.lr)  # type: ignore
        loss_function = nn.CrossEntropyLoss()

        # Format dataset for training
        formatted_dataset = format_dataset(dataset, log)
        num_batches = len(formatted_dataset) // config.batch_size

        inferred_device = next(self.orca_model.parameters()).device
        # Training loop
        if validation_dataset is not None:
            # Save the model before finetuning with validation
            # so we can revert if the validation loss increases in the first epoch
            eval_result = self.evaluate(validation_dataset, log=log, curate=False)
            validation_scores.append(eval_result.loss)
            self.save(f"finetune-{current_finetune_uuid}.pth")
        for epoch in range(config.epochs):
            total_loss = 0.0
            self.logger.info(f"Epoch {epoch + 1}/{config.epochs}") if log else None
            if stop_early:
                self.logger.info("Stopping Early") if log else None
                break

            # Reset gradients at the beginning of each epoch
            optimizer.zero_grad()

            for i in tqdm(range(num_batches), desc=f"Finetuning Epoch:{epoch + 1}", disable=not log):
                # Batch preparation
                batch_data = formatted_dataset[i * config.batch_size : (i + 1) * config.batch_size]
                labels = torch.LongTensor([data[1] for data in batch_data])

                # Move tensors to the appropriate device
                inputs = [data[0] for data in batch_data]
                labels = labels.to(inferred_device)

                # Forward pass: get predictions
                predictions = self.predict_batch(inputs, log=False, curate=False)

                # Extract logits from PredictionResult and stack them
                logits = torch.stack([torch.Tensor(pred.logits).to(inferred_device) for pred in predictions])

                # Compute loss
                loss = loss_function(logits, labels)
                # Normalize the loss to account for gradient accumulation
                loss = loss / config.gradient_accumulation_steps
                total_loss += loss.item() * config.gradient_accumulation_steps

                # Backward pass
                loss.backward()

                # Gradient accumulation
                if (i + 1) % config.gradient_accumulation_steps == 0 or (i + 1) == num_batches:
                    optimizer.step()
                    optimizer.zero_grad()

                batch_count += 1

                if plot and fig_widget and plotter:
                    # Update data lists
                    fractional_epochs.append((batch_count + 1) / num_batches)
                    loss_values.append(loss.item())
                    total_loss_values.append(total_loss)
                    if show_running_mean:
                        mean_loss_values.append(mean(loss_values))
                    else:
                        mean_loss_values.append(mean(loss_values[-10:]))

                    # Update the plot
                    plotter.update(
                        fractional_epochs,
                        loss_values,
                        mean_loss_values,
                        validation_scores,
                        batch_count,
                        num_batches,
                        epoch,
                        config.epochs,
                    )

            avg_loss = total_loss / num_batches
            self.logger.info(f"Epoch {epoch + 1}, Loss: {avg_loss:.4f}") if log else None
            # run eval on validation set (when present) & record results
            if validation_dataset is not None:
                eval_result = self.evaluate(validation_dataset, log=log, curate=False)
                if validation_scores and eval_result.loss > validation_scores[-1] * 1.001:
                    stop_early = True
                    self.logger.info(f"Stopping Early: {eval_result.loss} > {validation_scores[-1]}") if log else None
                    validation_scores.append(eval_result.loss)
                    if plotter and fig_widget:
                        plotter.update(
                            fractional_epochs,
                            loss_values,
                            mean_loss_values,
                            validation_scores,
                            batch_count,
                            num_batches,
                            epoch,
                            config.epochs,
                        )
                        fig_widget.add_vline(
                            x=int((batch_count + 1) / num_batches),
                            line_color="rgba(255,0,0,0.25)",
                        )
                    self.load(f"finetune-{current_finetune_uuid}.pth")
                else:
                    validation_scores.append(eval_result.loss)
                    self.save(f"finetune-{current_finetune_uuid}.pth")

        self.logger.info("Fine-tuning completed") if log else None

    def save(self, path: str):
        """Saves the model to a file using safetensors"""
        assert isinstance(self.orca_model, nn.Module)

        # Prepare the state dict
        state_dict = self.orca_model.state_dict()
        # Convert non-contiguous tensors to contiguous tensors in the state dict
        contiguous_state_dict = {k: v.contiguous() if not v.is_contiguous() else v for k, v in state_dict.items()}

        # Prepare metadata
        metadata = {
            "head_model": self.orca_model.model_properties.name,
            "embedding_model": self.base_model.name,
            "head_model_version": self.orca_model.model_properties.version,
        }

        # Convert all metadata values to strings
        metadata = {k: str(v) for k, v in metadata.items()}

        # Save using safetensors
        save_file(contiguous_state_dict, path, metadata=metadata)

        self.logger.info("Model saved successfully using safetensors")

    def load(self, path: str):
        """Loads a model from a safetensors file, verifying that the model is compatible with the current instance"""
        # Load the state dict and metadata using safetensors
        state_dict = load_file(path)
        metadata = safe_open(path, framework="pt").metadata()  # type: ignore - metadata is present

        # Verify model compatibility
        if metadata["head_model"] != self.orca_model.model_properties.name:
            raise ValueError(
                f"Head Model mismatch: {metadata['head_model']} != {self.orca_model.model_properties.name}"
            )
        if metadata["embedding_model"] != self.base_model.name:
            raise ValueError(f"Embedding Model mismatch: {metadata['embedding_model']} != {self.base_model.name}")
        if metadata["head_model_version"] != str(self.orca_model.model_properties.version):
            raise ValueError(
                f"Head Model version mismatch: {metadata['head_model_version']} != {self.orca_model.model_properties.version}"
            )

        # Load the state dict into the model
        assert isinstance(self.orca_model, nn.Module)
        self.orca_model.load_state_dict(state_dict)
        self.logger.info("Model loaded successfully from safetensors file")

    def use(self, memoryset: LabeledMemoryset):
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

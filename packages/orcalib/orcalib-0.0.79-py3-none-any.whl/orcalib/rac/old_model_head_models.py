from dataclasses import dataclass
from typing import Protocol, cast

import torch
import torch.nn.functional as F
from torch import Tensor, nn
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    PreTrainedTokenizerBase,
)
from typing_extensions import deprecated

from orcalib.memoryset import InputTypeList

# TODO: utils for memory and label tensor construction (including unit tests)


@dataclass(frozen=True)
class HeadModelProperties:
    needs_memories: bool
    name: str
    version: int
    needs_original_data: bool


@dataclass(frozen=True)
class RACHeadInitConfig:
    embedding_dim: int
    num_classes: int
    cross_encoder_model: str | None = None
    master_dropout: float = 0.1


# TODO: this is easy to understand, but comparatively slow. Use vector ops instead (via F.one_hot)
def _build_one_hot_label_tensor(labels: list[list[int]], num_classes: int) -> Tensor:
    label_tensor = torch.zeros(len(labels), len(labels[0]), num_classes)
    for i, label_list in enumerate(labels):
        for j, label in enumerate(label_list):
            label_tensor[i, j, label] = 1
    return label_tensor


def _build_memory_tensor(memories: list[list[Tensor]]) -> Tensor:
    return torch.stack([torch.stack(memory, dim=1) for memory in memories])


class RACHeadProtocol(Protocol):
    last_memory_weights: torch.Tensor | None = None

    def __init__(self, config: RACHeadInitConfig):
        pass

    # TODO: add attention weights return to the forward method
    def forward(
        self,
        input_embeddings: Tensor,
        memory_embeddings: list[list[Tensor]],
        memory_labels: list[list[int]],
        original_input: InputTypeList,
        original_memories: list[InputTypeList],
    ) -> Tensor:
        """
        Forward pass of the model.
        Args:
            input_embeddings (Tensor): The input embeddings.
            memory_embeddings (list[Tensor]): The embeddings of the memories.
            memory_labels (list[list[int]]): The labels of the memories.
            original_input (InputListType): The original (non-embedded) input examples.
            original_memories (list[InputListType]): The original (non-embedded) memories.
        Returns:
            Tensor: Result Logits.
        """
        ...

    @property
    def model_properties(self) -> HeadModelProperties:
        ...


@deprecated("Use FeedForwardClassificationHead instead")
class SimpleClassifier(nn.Module):
    last_memory_weights: torch.Tensor | None = None

    def __init__(self, config: RACHeadInitConfig):
        super().__init__()
        self.head = nn.Sequential(
            nn.Linear(config.embedding_dim, config.embedding_dim),
            nn.ReLU(),
            nn.LayerNorm(config.embedding_dim),
            nn.Linear(config.embedding_dim, config.embedding_dim),
            nn.ReLU(),
            nn.Linear(config.embedding_dim, config.num_classes),
            nn.Softmax(dim=1),
        )

    def forward(
        self,
        input_embeddings: Tensor,
        memory_embeddings: list[list[Tensor]],
        memory_labels: list[list[int]],
        original_input: InputTypeList,
        original_memories: list[InputTypeList],
    ) -> Tensor:
        return self.head(input_embeddings)

    @property
    def model_properties(self) -> HeadModelProperties:
        return HeadModelProperties(needs_memories=False, needs_original_data=False, version=1, name="SimpleClassifier")


@deprecated("Use MemoryMixtureOfExpertsClassificationHead instead")
class SimpleMMOEHead(nn.Module):
    last_memory_weights: torch.Tensor | None = None

    def __init__(self, config: RACHeadInitConfig):
        super().__init__()
        init_tensor = torch.nn.init.orthogonal_(torch.empty(config.embedding_dim, config.embedding_dim))
        self.W_Q = nn.Parameter(init_tensor.clone().T)
        self.W_K = nn.Parameter(init_tensor.clone())
        self.config = config

    def forward(
        self,
        input_embeddings: Tensor,
        memory_embeddings: list[list[Tensor]],
        memory_labels: list[list[int]],
        original_input: InputTypeList,
        original_memories: list[InputTypeList],
    ) -> Tensor:
        memory_tensor = _build_memory_tensor(memory_embeddings)
        label_tensor = _build_one_hot_label_tensor(memory_labels, self.config.num_classes)

        # TODO: test normalization of query_embeddings and key_embedding
        memory_weights = F.leaky_relu(torch.bmm((input_embeddings @ self.W_K).unsqueeze(1), self.W_Q @ memory_tensor))
        self.last_memory_weights = memory_weights

        # TODO: How to run Z through more nonlinearity? (would require fixed mmoe width? or maybe just a 1x1 linear layer stack? layer-norm with 1d?)
        # TODO: information crossover between memory embeddings
        # TODO: test this without the final softmax
        # TODO: make this more efficient by leveraging that value_labels are one_hot tensors
        return F.softmax(torch.bmm(memory_weights, label_tensor.to(memory_weights.dtype)).squeeze(1), dim=1)

    @property
    def model_properties(self) -> HeadModelProperties:
        return HeadModelProperties(needs_memories=True, needs_original_data=False, version=1, name="SimpleMMOEHead")


# TODO: move an equivalent into torch_layers
class MCERHead(nn.Module):
    def __init__(self, config: RACHeadInitConfig):
        super().__init__()
        if config.cross_encoder_model is None:
            raise ValueError("MCERHead requires specifying a cross_encoder_model")
        self.tokenizer: PreTrainedTokenizerBase = AutoTokenizer.from_pretrained(config.cross_encoder_model)
        self.cross_encoder = AutoModelForSequenceClassification.from_pretrained(
            config.cross_encoder_model, num_labels=1, trust_remote_code=True
        )
        self.config = config

    def compute_score(self, original_input: InputTypeList, original_memory: InputTypeList) -> Tensor:
        assert isinstance(original_input[0], str) and isinstance(
            original_memory[0], str
        ), "CrossEncoderHead only works with text input for now"

        tokens = self.tokenizer(
            cast(list[str], original_input),
            cast(list[str], original_memory),
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return self.cross_encoder(**tokens.to(self.cross_encoder.device)).logits.squeeze()

    def forward(
        self,
        input_embeddings: Tensor,
        memory_embeddings: list[list[Tensor]],
        memory_labels: list[list[int]],
        original_input: InputTypeList,
        original_memories: list[InputTypeList],
    ) -> Tensor:
        batch_size = len(memory_labels)
        num_memories = len(memory_labels[0])
        # compute weights for each memory withe the cross encoder
        memory_weights = torch.stack(
            [
                self.compute_score([original_input[i]] * num_memories, memory_texts)
                for i, memory_texts in enumerate(original_memories)
            ],
            dim=0,
        )  # batch_size x num_memories
        self.last_memory_weights = memory_weights
        # compute logits as weighted sum of memory labels
        logits = torch.zeros(
            batch_size, self.config.num_classes, device=memory_weights.device
        )  # batch_size x num_classes
        logits.scatter_add_(1, torch.tensor(memory_labels), memory_weights)

        logits = logits.softmax(dim=-1)
        return logits

    @property
    def model_properties(self) -> HeadModelProperties:
        return HeadModelProperties(needs_memories=True, needs_original_data=True, version=1, name="CrossEncoderHead")

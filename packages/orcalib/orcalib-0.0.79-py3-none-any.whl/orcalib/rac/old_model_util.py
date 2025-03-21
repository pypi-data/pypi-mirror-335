import logging
from typing import cast

import pandas as pd
from datasets import Dataset
from PIL import Image
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset
from tqdm.auto import tqdm

from ..memoryset.memory_types import InputType, LabeledMemory

logger = logging.getLogger(__name__)


DatasetLike = (
    list[tuple[InputType, int]]
    | list[tuple[str, int]]
    | list[tuple[Image.Image, int]]
    | pd.DataFrame
    | Dataset
    | TorchDataset
    | TorchDataLoader
    | LabeledMemory
    | list[LabeledMemory]
    | dict
    | list[dict]
)


def format_dataset(dataset: DatasetLike, log: bool = False) -> list[tuple[InputType, int]]:
    from orcalib.memoryset import LabeledMemory

    if isinstance(dataset, pd.DataFrame):
        return _format_pandas_dataframe(dataset, log)
    elif isinstance(dataset, Dataset):
        return _format_huggingface_dataset(dataset, log)
    elif isinstance(dataset, TorchDataset):
        return _format_pytorch_dataset(dataset, log)
    elif isinstance(dataset, TorchDataLoader):
        return _format_pytorch_dataloader(dataset, log)
    elif isinstance(dataset, dict):
        return _format_list_of_dicts([dataset], log)
    elif isinstance(dataset, LabeledMemory):
        return _format_memories([dataset], log)
    elif isinstance(dataset, list):
        if isinstance(dataset[0], dict):
            return _format_list_of_dicts(cast(list[dict], dataset), log)
        elif isinstance(dataset[0], LabeledMemory):
            return _format_memories(cast(list[LabeledMemory], dataset), log)
        elif isinstance(dataset[0], tuple) and len(dataset[0]) == 2:
            # Handle list of tuples: no op.
            return cast(list[tuple[InputType, int]], dataset)
        else:
            raise TypeError(f"Unsupported dataset format: {type(dataset[0])}")
    else:
        raise TypeError("Unsupported dataset format")


def to_dataset(data: DatasetLike) -> Dataset:
    if isinstance(data, Dataset) and "value" in data.features and "label" in data.features:
        return data.select_columns(["value", "label"])
    transformed_data = format_dataset(data)
    return Dataset.from_dict(
        {
            "value": [cast(InputType, m[0]) for m in transformed_data],
            "label": [m[1] for m in transformed_data],
        }
    )


def _format_memories(dataset: list["LabeledMemory"], log: bool) -> list[tuple[InputType, int]]:
    formatted_dataset: list[tuple[InputType, int]] = []
    for row in tqdm(dataset, total=len(dataset), desc="Formatting Memory Fragments", disable=not log):
        formatted_dataset.append((row.value, row.label))
    return formatted_dataset


def _format_list_of_dicts(dataset: list[dict], log: bool) -> list[tuple[InputType, int]]:
    formatted_dataset: list[tuple[InputType, int]] = []
    for row in tqdm(dataset, total=len(dataset), desc="Formatting List of Dicts", disable=not log):
        if "value" in row and "label" in row:
            value = row["value"]
            label = row["label"]
        elif "image" in row and "label" in row:
            value = row["image"]
            label = row["label"]
        elif "text" in row and "label" in row:
            value = row["text"]
            label = row["label"]
        elif "label" in row and len(row) == 2:
            label = row["label"]
            del row["label"]
            value = row[[row.keys()][0]]
        else:
            raise TypeError("List of dicts does not contain 'value' and 'label' columns")

        formatted_dataset.append((value, label))
    return formatted_dataset


def _format_pandas_dataframe(dataset: pd.DataFrame, log: bool) -> list[tuple[InputType, int]]:
    formatted_dataset: list[tuple[InputType, int]] = []
    for _, row in tqdm(dataset.iterrows(), total=len(dataset), desc="Formatting Pandas DataFrame", disable=not log):
        if "value" in row and "label" in row:
            value = cast(InputType, row["value"])
            label = cast(int, row["label"])
        elif "image" in row and "label" in row:
            value = cast(InputType, row["image"])
            label = cast(int, row["label"])
        elif "text" in row and "label" in row:
            value = cast(InputType, row["text"])
            label = cast(int, row["label"])
        elif "label" in row and row.shape[0] == 2:
            value = cast(InputType, row.drop("label").iloc[0])
            label = cast(int, row["label"])
        else:
            raise TypeError("DataFrame does not contain 'value' and 'label' columns")

        formatted_dataset.append((value, label))
    return formatted_dataset


def _format_huggingface_dataset(dataset: Dataset, log: bool) -> list[tuple[InputType, int]]:
    formatted_dataset: list[tuple[InputType, int]] = []
    # Check if the dataset supports string-based indexing
    if all(isinstance(row, dict) for row in dataset):
        for row in tqdm(dataset, total=len(dataset), desc="Formatting Huggingface Dataset", disable=not log):
            if "value" in row and "label" in row and isinstance(row, dict):
                value = row["value"]
                label = row["label"]
            elif "image" in row and "label" in row and isinstance(row, dict):
                value = row["image"]
                label = row["label"]
            elif "text" in row and "label" in row and isinstance(row, dict):
                value = row["text"]
                label = row["label"]
            elif "label" in row and isinstance(row, dict) and len(row.keys()) == 2:
                label = row["label"]
                value = [v for k, v in row.items() if k != "label"][0]
            else:
                raise TypeError("Dataset does not contain 'value' and 'label' columns")

            formatted_dataset.append((value, label))
    else:
        # Handle the case where the dataset does not support string-based indexing
        raise TypeError("Dataset does not support string-based indexing")
    return formatted_dataset


def _format_pytorch_dataset(dataset: TorchDataset, log: bool) -> list[tuple[InputType, int]]:
    formatted_dataset: list[tuple[InputType, int]] = []
    dataset_list = [item for item in dataset]
    for row in tqdm(dataset_list, total=len(dataset_list), desc="Formatting PyTorch Dataset", disable=not log):
        if "value" in row and "label" in row:
            value = row["value"]
            label = row["label"]
        elif "image" in row and "label" in row:
            value = row["image"]
            label = row["label"]
        elif "text" in row and "label" in row:
            value = row["text"]
            label = row["label"]
        elif "label" in row and "value" not in row and len(row) == 2:
            label = row["label"]
            value = [v for k, v in row.items() if k != "label"][0]
        else:
            raise TypeError("PyTorch Dataset does not contain 'value' and 'label' columns")

        formatted_dataset.append((value, label))
    return formatted_dataset


def _format_pytorch_dataloader(dataset: TorchDataLoader, log: bool) -> list[tuple[InputType, int]]:
    formatted_dataset: list[tuple[InputType, int]] = []
    for row in tqdm(dataset, total=len(dataset), desc="Formatting PyTorch Dataloader", disable=not log):
        if "value" in row and "label" in row:
            value = row["value"][0]
            label = row["label"].item()
        elif "image" in row and "label" in row:
            value = row["image"][0]
            label = row["label"].item()
        elif "text" in row and "label" in row:
            value = row["text"][0]
            label = row["label"].item()
        elif "label" in row and "value" not in row and len(row) == 2:
            label = row["label"].item()
            value = [v for k, v in row.items() if k != "label"][0][0]
        else:
            raise TypeError("PyTorch Dataloader does not contain 'value' and 'label' columns")

        formatted_dataset.append((value, label))
    return formatted_dataset

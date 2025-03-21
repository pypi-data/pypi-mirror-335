import pandas as pd
import pytest
from datasets import ClassLabel, Dataset, Features, Value
from torch.utils.data import DataLoader as TorchDataLoader
from torch.utils.data import Dataset as TorchDataset

from ..memoryset import InputType
from .old_model_util import format_dataset

#################### Formatting Dataset Tests ####################

# Sample data
data_dict = {
    "value": ["test", "bread", "air", "bread", "test"],
    "label": [0, 1, 2, 1, 0],
}

data_dict_image = {
    "image": ["test", "bread", "air", "bread", "test"],
    "label": [0, 1, 2, 1, 0],
}

data_dict_text = {
    "text": ["test", "bread", "air", "bread", "test"],
    "label": [0, 1, 2, 1, 0],
}

tuple_dataset: list[tuple[InputType, int]] = [
    ("test", 0),
    ("bread", 1),
    ("air", 2),
    ("bread", 1),
    ("test", 0),
]


def test_format_dataset_accepts_tuple():
    formatted_dataset = format_dataset(tuple_dataset)
    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_dataframe():
    data = [
        {"value": "test", "label": 0},
        {"value": "bread", "label": 1},
        {"value": "air", "label": 2},
        {"value": "bread", "label": 1},
        {"value": "test", "label": 0},
    ]

    dataframe = pd.DataFrame(data)

    formatted_dataset = format_dataset(dataset=dataframe)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_dataframe_with_image_key():
    data = [
        {"image": "test", "label": 0},
        {"image": "bread", "label": 1},
        {"image": "air", "label": 2},
        {"image": "bread", "label": 1},
        {"image": "test", "label": 0},
    ]

    dataframe = pd.DataFrame(data)

    formatted_dataset = format_dataset(dataset=dataframe)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_dataframe_with_text_key():
    data = [
        {"text": "test", "label": 0},
        {"text": "bread", "label": 1},
        {"text": "air", "label": 2},
        {"text": "bread", "label": 1},
        {"text": "test", "label": 0},
    ]

    dataframe = pd.DataFrame(data)

    formatted_dataset = format_dataset(dataset=dataframe)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_partially_labeled_pandas_dataframe():
    data = [
        {"input": "test", "label": 0},
        {"input": "bread", "label": 1},
        {"input": "air", "label": 2},
        {"input": "bread", "label": 1},
        {"input": "test", "label": 0},
    ]

    dataframe = pd.DataFrame(data)

    formatted_dataset = format_dataset(dataset=dataframe)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_partially_labeled_HF_dataset():
    # Define the features
    features = Features(
        {
            "input": Value(dtype="string"),
            "label": ClassLabel(names=["test", "bread", "air"]),
        }
    )

    one_label_data_dict = {
        "input": ["test", "bread", "air", "bread", "test"],
        "label": [0, 1, 2, 1, 0],
    }
    # Create the dataset
    hf_dataset = Dataset.from_dict(one_label_data_dict, features=features)

    formatted_dataset = format_dataset(dataset=hf_dataset)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_HF_dataset():
    # Define the features
    features = Features(
        {
            "value": Value(dtype="string"),
            "label": ClassLabel(names=["test", "bread", "air"]),
        }
    )

    # Create the dataset
    hf_dataset = Dataset.from_dict(data_dict, features=features)

    formatted_dataset = format_dataset(dataset=hf_dataset)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_HF_dataset_with_image_key():
    # Define the features
    features = Features(
        {
            "image": Value(dtype="string"),
            "label": ClassLabel(names=["test", "bread", "air"]),
        }
    )
    hf_dataset = Dataset.from_dict(data_dict_image, features=features)

    formatted_dataset = format_dataset(dataset=hf_dataset)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_HF_dataset_with_text_key():
    # Define the features
    features = Features(
        {
            "text": Value(dtype="string"),
            "label": ClassLabel(names=["test", "bread", "air"]),
        }
    )
    hf_dataset = Dataset.from_dict(data_dict_text, features=features)

    formatted_dataset = format_dataset(dataset=hf_dataset)

    assert formatted_dataset == tuple_dataset


def test_format_dataset_accepts_pytorch_dataset_and_dataloader():
    class TorchDatasetSubclassed(TorchDataset):
        def __init__(self, value, label):
            self.value = value
            self.label = label

        def __getitem__(self, idx):
            return {"value": self.value[idx], "label": self.label[idx]}

        def __len__(self):
            return len(self.value)

    torch_dataset = TorchDatasetSubclassed(value=data_dict["value"], label=data_dict["label"])

    torch_dataloader = TorchDataLoader(torch_dataset, batch_size=1)
    formatted_dataloader = format_dataset(dataset=torch_dataloader)
    formatted_torch_dataset = format_dataset(dataset=torch_dataset)

    assert formatted_dataloader == tuple_dataset
    assert formatted_torch_dataset == tuple_dataset


def test_format_dataset_accepts_partially_labeled_pytorch_dataset_and_dataloader():
    class TorchDatasetSubclassed(TorchDataset):
        def __init__(self, input, label):
            self.input = input
            self.label = label

        def __getitem__(self, idx):
            return {"input": self.input[idx], "label": self.label[idx]}

        def __len__(self):
            return len(self.input)

    torch_dataset = TorchDatasetSubclassed(input=data_dict["value"], label=data_dict["label"])

    torch_dataloader = TorchDataLoader(torch_dataset, batch_size=1)
    formatted_torch_dataloader = format_dataset(dataset=torch_dataloader)
    formatted_torch_dataset = format_dataset(dataset=torch_dataset)

    assert formatted_torch_dataloader == tuple_dataset
    assert formatted_torch_dataset == tuple_dataset


def test_format_dataset_raises_when_given_tuple_with_greater_than_2_columns():
    bad_tuple_dataset = [
        ("test", 0, "extra"),
        ("bread", 1, "extra"),
        ("air", 2, "extra"),
        ("bread", 1, "extra"),
        ("test", 0, "extra"),
    ]

    with pytest.raises(TypeError):
        format_dataset(bad_tuple_dataset)  # type: ignore


def test_format_dataset_accepts_dict():
    data = [
        {"value": "test", "label": 0},
        {"value": "bread", "label": 1},
        {"value": "air", "label": 2},
        {"value": "bread", "label": 1},
        {"value": "test", "label": 0},
    ]

    formatted_dataset = format_dataset(dataset=data)

    assert [formatted_dataset[0]] == format_dataset(dataset=data[0])
    assert formatted_dataset == format_dataset(dataset=data)


def test_format_dataset_accepts_dict_with_image_key():
    data = [
        {"image": "test", "label": 0},
        {"image": "bread", "label": 1},
        {"image": "air", "label": 2},
        {"image": "bread", "label": 1},
        {"image": "test", "label": 0},
    ]

    formatted_dataset = format_dataset(dataset=data)

    assert [formatted_dataset[0]] == format_dataset(dataset=data[0])
    assert formatted_dataset == format_dataset(dataset=data)


def test_format_dataset_accepts_dict_with_text_key():
    data = [
        {"text": "test", "label": 0},
        {"text": "bread", "label": 1},
        {"text": "air", "label": 2},
        {"text": "bread", "label": 1},
        {"text": "test", "label": 0},
    ]

    formatted_dataset = format_dataset(dataset=data)

    assert [formatted_dataset[0]] == format_dataset(dataset=data[0])
    assert formatted_dataset == format_dataset(dataset=data)

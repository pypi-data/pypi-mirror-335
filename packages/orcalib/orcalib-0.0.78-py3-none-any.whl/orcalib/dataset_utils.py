import hashlib
import logging
from typing import Any

from datasets import ClassLabel, Dataset, Image, Value
from PIL import Image as pil

from .pydantic_utils import ColumnInfo, ColumnType


def parse_dataset(
    dataset: Dataset,
    *,
    value_column: str,
    label_column: str | None = None,
    score_column: str | None = None,
    source_id_column: str | None = None,
    other_columns_as_metadata: bool = False,
) -> Dataset:
    """
    Transforms a dataset to have canonical value, label, score, source_id, and metadata columns or raises an error

    Args:
        dataset: The dataset to transform
        value_column: The name of the column containing the string or image values to embed
        label_column: Optional name of the column containing the integer labels
        score_column: Optional name of the column containing the float scores
        source_id_column: Optional name of a column containing unique IDs for each data point in a system of reference
        other_columns_as_metadata: Optionally collect all other column values in a dictionary in the metadata column

    Returns:
        The transformed dataset which is guaranteed to have the following features:
            - 'value' image column or string value column
            - 'label' class label column or integer value column (optional)
            - 'score' float value column (optional)
            - 'source_id' string value column (optional)
            - 'metadata' dictionary column (optional)

    Raises:
        ValueError: If the specified columns are not found or have the wrong data type
    """
    out_dataset = dataset
    columns_to_keep = ["value"]

    # validate value column
    if value_column not in dataset.features:
        raise ValueError(f"Specified value column `{value_column}` not found in dataset")
    if not (
        isinstance(dataset.features[value_column], Image)
        or (isinstance(dataset.features[value_column], Value) and dataset.features[value_column].dtype == "string")
    ):
        raise ValueError(f"The specified value column `{value_column}` must be of type string or image")

    if value_column != "value":
        out_dataset = out_dataset.rename_column(value_column, "value")
    # ensure image is decoded if value column is image
    if isinstance(out_dataset.features["value"], Image) and not out_dataset.features["value"].decode:
        out_dataset = out_dataset.cast_column("value", Image(decode=True))

    # validate label column
    if label_column is not None:
        if label_column not in dataset.features:
            raise ValueError(f"Specified label column `{label_column}` not found in dataset")
        if not (
            (
                isinstance(dataset.features[label_column], Value)
                or isinstance(dataset.features[label_column], ClassLabel)
            )
            and dataset.features[label_column].dtype == "int64"
        ):
            raise ValueError(f"The specified label column `{label_column}` must be of type int64")

        columns_to_keep.append("label")
        if label_column != "label":
            out_dataset = out_dataset.rename_column(label_column, "label")

    # validate score column
    if score_column is not None:
        if score_column not in dataset.features:
            raise ValueError(f"Specified score column `{score_column}` not found in dataset")
        if not (
            isinstance(dataset.features[score_column], Value)
            and dataset.features[score_column].dtype in ("float32", "float64")
        ):
            raise ValueError(f"The specified score column `{score_column}` must be of type float")

        columns_to_keep.append("score")
        if score_column != "score":
            out_dataset = out_dataset.rename_column(score_column, "score")

    # add source ID column if specified
    if source_id_column:
        if source_id_column not in dataset.features:
            raise ValueError(f"Specified source ID column `{source_id_column}` not found in dataset")
        if dataset.features[source_id_column].dtype != "string":
            raise ValueError(f"The specified source ID column `{source_id_column}` must be of type string")
        if source_id_column != "source_id":
            out_dataset = out_dataset.rename_column(source_id_column, "source_id")
        columns_to_keep.append("source_id")

    # add metadata column if specified
    if other_columns_as_metadata:
        incompatible_columns = [
            k for k, v in dataset.features.items() if k not in columns_to_keep and not isinstance(v, Value)
        ]
        if len(incompatible_columns) > 0:
            logging.warning(f"Excluding non-scalar columns {', '.join(incompatible_columns)} from metadata: ")
        out_dataset = out_dataset.map(
            lambda x: {"metadata": {k: v for k, v in x.items() if k not in columns_to_keep + incompatible_columns}}
        )
        columns_to_keep.append("metadata")

    return out_dataset.select_columns(columns_to_keep)


def parse_label_names(dataset: Dataset, *, label_column: str) -> list[str] | None:
    """
    Parses the label names from a dataset if the label column is a ClassLabel

    Args:
        dataset: The dataset to parse
        label_column: The name of the column containing the class labels

    Returns:
        The list of label names or None if the label column is not a ClassLabel
    """
    if isinstance(dataset.features[label_column], ClassLabel):
        return dataset.features[label_column].names
    return None


def parse_dataset_schema(dataset: Dataset) -> list[ColumnInfo]:
    features = dataset.features

    def get_type(feature) -> ColumnType:
        match feature:
            case Value() if feature.dtype == "string":
                return ColumnType.STRING
            case Value() if "float" in feature.dtype:
                return ColumnType.FLOAT
            case Value() if "int" in feature.dtype:
                return ColumnType.INT
            case Value() if feature.dtype == "bool":
                return ColumnType.BOOL
            case ClassLabel():
                return ColumnType.ENUM
            case Image():
                return ColumnType.IMAGE
            case _:
                return ColumnType.OTHER

    return [
        ColumnInfo(
            name=name,
            type=get_type(feature),
            enum_options=feature.names if isinstance(feature, ClassLabel) else None,
        )
        for name, feature in features.items()
    ]


def remove_duplicates(dataset: Dataset, column: str) -> Dataset:
    """
    Removes all duplicate rows from a dataset based on the values in a column.

    Params:
        dataset: The dataset to remove duplicates from.
        column: The column to remove duplicates from.

    Returns:
        The dataset with duplicates removed.
    """

    def get_hash(example: dict[str, Any]):
        value = example[column]
        if isinstance(value, pil.Image):
            hash = hashlib.md5(value.convert("RGB").tobytes()).hexdigest()
        elif isinstance(value, str):
            hash = hashlib.md5(value.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        return {"hash": hash}

    dataset = dataset.map(get_hash)
    uniques = set(dataset["hash"])

    def check_uniques(example: dict[str, Any]) -> bool:
        """Check if current hash is still in set of unique hashes and remove if true."""
        if example["hash"] in uniques:
            uniques.remove(example["hash"])
            return True
        else:
            return False

    return dataset.filter(lambda example: check_uniques(example)).remove_columns(["hash"])

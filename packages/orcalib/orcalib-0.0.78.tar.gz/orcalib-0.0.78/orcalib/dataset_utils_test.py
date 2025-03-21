import base64
from io import BytesIO

import pytest
from datasets import ClassLabel, Dataset, Image, Value
from PIL import Image as pil

from orcalib.pydantic_utils import ColumnInfo, ColumnType

from .dataset_utils import (
    parse_dataset,
    parse_dataset_schema,
    parse_label_names,
    remove_duplicates,
)


def test_parse_dataset_with_text():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    parsed = parse_dataset(dataset, value_column="text")
    assert "value" in parsed.features
    assert parsed.features["value"].dtype == "string"
    assert len(parsed) == 2
    assert len(parsed.features) == 1


def test_parse_dataset_with_pil_image():
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="
    bytes_image: bytes = base64.b64decode(base64_image)
    pil_image: pil.Image = pil.open(BytesIO(bytes_image))
    dataset = Dataset.from_list([{"image": pil_image}])
    parsed = parse_dataset(dataset, value_column="image")
    assert "value" in parsed.features
    assert isinstance(parsed.features["value"], Image)
    assert parsed[0]["value"] == pil_image
    assert len(parsed.features) == 1


def test_parse_dataset_with_bytes_image():
    base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAJCAIAAABv85FHAAAAN0lEQVR4nGP8//8/Aw7AgmAyMkIZMNVM6BJIbCZ0CSRpJnRRJEBQDtOp//8j6UOWhrFZMIXgAABurQ8RDsBcHQAAAABJRU5ErkJggg=="
    bytes_image: bytes = base64.b64decode(base64_image)
    pil_image: pil.Image = pil.open(BytesIO(bytes_image))
    dataset = Dataset.from_list([{"image": {"bytes": bytes_image}}]).cast_column("image", Image(decode=False))
    parsed = parse_dataset(dataset, value_column="image")
    assert "value" in parsed.features
    assert isinstance(parsed.features["value"], Image)
    assert parsed[0]["value"] == pil_image
    assert len(parsed.features) == 1


def test_parse_dataset_missing_value_column():
    dataset = Dataset.from_dict({"other": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text")


def test_parse_dataset_wrong_value_column_type():
    dataset = Dataset.from_dict({"value": [1, 2]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="value")


def test_parse_dataset_with_int_label():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": [0, 1]})
    parsed = parse_dataset(dataset, value_column="text", label_column="label")
    assert "label" in parsed.features
    assert isinstance(parsed.features["label"], Value)
    assert parsed.features["label"].dtype == "int64"
    assert len(parsed) == 2
    assert len(parsed.features) == 2


def test_parse_dataset_with_class_label():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": ["pos", "neg"]}).cast_column(
        "label", ClassLabel(num_classes=2, names=["neg", "pos"])
    )
    parsed = parse_dataset(dataset, value_column="text", label_column="label")
    assert "label" in parsed.features
    assert isinstance(parsed.features["label"], ClassLabel)
    assert len(parsed) == 2
    assert len(parsed.features) == 2
    assert parsed[0]["label"] == 1
    assert parsed[1]["label"] == 0


def test_parse_dataset_missing_label_column():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", label_column="label")


def test_parse_dataset_wrong_label_column_type():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "label": ["pos", "neg"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", label_column="label")


def test_parse_dataset_with_float_score():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "score": [0.5, 1.0]})
    parsed = parse_dataset(dataset, value_column="text", score_column="score")
    assert "score" in parsed.features
    assert isinstance(parsed.features["score"], Value)
    assert parsed.features["score"].dtype in ("float32", "float64")
    assert len(parsed) == 2
    assert len(parsed.features) == 2


def test_parse_dataset_missing_score_column():
    dataset = Dataset.from_dict({"text": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", score_column="score")


def test_parse_dataset_wrong_score_column_type():
    dataset = Dataset.from_dict({"text": ["hello", "world"], "score": ["high", "low"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="text", score_column="score")


def test_parse_dataset_with_string_source_id():
    dataset = Dataset.from_dict({"value": ["hello", "world"], "label": [0, 1], "source_id": ["a:1", "b:2"]})
    parsed = parse_dataset(dataset, value_column="value", label_column="label", source_id_column="source_id")
    assert "source_id" in parsed.features
    assert parsed.features["source_id"].dtype == "string"
    assert len(parsed) == 2
    assert len(parsed.features) == 3


def test_parse_dataset_with_missing_source_id_column():
    dataset = Dataset.from_dict({"value": ["hello", "world"]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="value", source_id_column="source_id")


def test_parse_dataset_with_wrong_source_id_column_type():
    dataset = Dataset.from_dict({"value": ["hello", "world"], "source_id": [1, 2]})
    with pytest.raises(ValueError):
        parse_dataset(dataset, value_column="value", source_id_column="source_id")


def test_parse_dataset_with_other_columns_as_metadata():
    dataset = Dataset.from_dict(
        {
            "value": ["hello", "world"],
            "label": [0, 1],
            "score": [1.5, 2.5],
            "source_id": ["a:1", "b:2"],
            "metadata": ["some", "context"],
        }
    )
    parsed = parse_dataset(
        dataset,
        value_column="value",
        label_column="label",
        other_columns_as_metadata=True,
    )
    assert "metadata" in parsed.features
    assert len(parsed) == 2
    assert len(parsed.features) == 3
    assert parsed[0]["metadata"] == {"score": 1.5, "metadata": "some", "source_id": "a:1"}
    assert parsed[1]["metadata"] == {"score": 2.5, "metadata": "context", "source_id": "b:2"}


def test_parse_dataset_with_other_columns_as_metadata_and_invalid_types():
    dataset = Dataset.from_dict(
        {
            "value": ["hello", "world"],
            "label": [0, 1],
            "source_id": ["a:1", "b:2"],
            "invalid_metadata": [[1.5], [2.5]],
            "metadata": ["some", "context"],
        }
    )
    parsed = parse_dataset(
        dataset,
        value_column="value",
        label_column="label",
        other_columns_as_metadata=True,
    )
    assert "metadata" in parsed.features
    assert len(parsed) == 2
    assert len(parsed.features) == 3
    assert parsed[0]["metadata"] == {"metadata": "some", "source_id": "a:1"}
    assert parsed[1]["metadata"] == {"metadata": "context", "source_id": "b:2"}


def test_parse_dataset_with_source_id_and_other_columns_as_metadata():
    dataset = Dataset.from_dict(
        {
            "value": ["hello", "world"],
            "label": [0, 1],
            "score": [0.5, 1.0],
            "source_id": ["a:1", "b:2"],
            "other": [1.5, 2.5],
        }
    )
    parsed = parse_dataset(
        dataset,
        value_column="value",
        label_column="label",
        score_column="score",
        other_columns_as_metadata=True,
        source_id_column="source_id",
    )
    assert "metadata" in parsed.features
    assert len(parsed) == 2
    assert len(parsed.features) == 5
    assert "source_id" in parsed.features
    assert parsed[0]["metadata"] == {"other": 1.5}
    assert parsed[1]["metadata"] == {"other": 2.5}


def test_parse_label_names_from_class_label():
    dataset = Dataset.from_dict({"label": [0, 1]}).cast_column("label", ClassLabel(num_classes=2, names=["neg", "pos"]))
    assert parse_label_names(dataset, label_column="label") == ["neg", "pos"]


def test_parse_label_names_from_int_label():
    dataset = Dataset.from_dict({"label": [0, 1]})
    assert parse_label_names(dataset, label_column="label") is None


def test_parse_label_names_from_string_label():
    dataset = Dataset.from_dict({"label": ["neg", "pos"]})
    assert parse_label_names(dataset, label_column="label") is None


def test_parse_dataset_schema():
    dataset = Dataset.from_dict(
        {
            "text": ["hello", "world"],
            "score": [0.5, 1.0],
            "label": [0, 1],
            "list": [[1, 2], [3, 4]],
            "metadata": [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
            "image": [
                pil.new("RGB", (100, 100), color=(255, 0, 0)),
                pil.new("RGB", (100, 100), color=(0, 255, 0)),
            ],
        }
    )
    dataset = dataset.cast_column("label", ClassLabel(num_classes=2, names=["neg", "pos"]))
    columns = parse_dataset_schema(dataset)
    assert columns == [
        ColumnInfo(name="text", type=ColumnType.STRING, enum_options=None),
        ColumnInfo(name="score", type=ColumnType.FLOAT, enum_options=None),
        ColumnInfo(name="label", type=ColumnType.ENUM, enum_options=["neg", "pos"]),
        ColumnInfo(name="list", type=ColumnType.OTHER, enum_options=None),
        ColumnInfo(name="metadata", type=ColumnType.OTHER, enum_options=None),
        ColumnInfo(name="image", type=ColumnType.IMAGE, enum_options=None),
    ]


def test_remove_duplicates():
    dataset = Dataset.from_dict({"text": ["hello", "world", "hello", "world"], "label": [0, 0, 1, 1]})
    dataset = remove_duplicates(dataset, "text")
    assert len(dataset) == 2
    assert dataset["text"] == ["hello", "world"]
    assert dataset["label"] == [0, 0]


def test_remove_duplicate_images():
    dataset = Dataset.from_dict(
        {
            "image": [
                pil.new("RGB", (100, 100), color=(255, 0, 0)),
                pil.new("RGB", (100, 100), color=(0, 255, 0)),
                pil.new("RGB", (100, 100), color=(255, 0, 0)),
                pil.new("RGB", (100, 100), color=(0, 255, 0)),
            ],
            "label": [0, 0, 1, 1],
        }
    )
    dataset = remove_duplicates(dataset, "image")
    assert len(dataset) == 2
    assert dataset["label"] == [0, 0]

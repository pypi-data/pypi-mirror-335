from enum import StrEnum
import json
import os
from typing import Iterable, Mapping, Union

from ie_datasets.datasets.docred.schema import DocREDRelationType, DocREDSchema
from ie_datasets.datasets.docred.unit import DocREDUnit
from ie_datasets.util.env import get_cache_dir


class DocREDSplit(StrEnum):
    TRAIN_ANNOTATED = "train_annotated"
    TRAIN_DISTANT = "train_distant"
    DEV = "dev"
    TEST = "test"


def load_docred_schema() -> DocREDSchema:
    BASE_DOCRED_DIR = get_cache_dir(subpath="docred")
    RELATION_TYPES_GDRIVE_ID = "1y9A0zKrvETc1ddUFuFhBg3Xfr7FEL4dW"

    schema_path = os.path.join(BASE_DOCRED_DIR, "schema.json")
    if os.path.exists(schema_path):
        with open(schema_path, "r") as f:
            schema = DocREDSchema.model_validate_json(f.read(), strict=True)
            return schema

    else:
        relation_types_path = os.path.join(BASE_DOCRED_DIR, "raw/relation_types.json")
        os.makedirs(os.path.dirname(relation_types_path), exist_ok=True)
        if not os.path.exists(relation_types_path):
            import gdown
            gdown.download(id=RELATION_TYPES_GDRIVE_ID, output=relation_types_path)
        with open(relation_types_path, "r") as f:
            relation_types_json = json.load(f)
            assert isinstance(relation_types_json, dict)

        relation_types = [
            DocREDRelationType(id=key, description=value)
            for key, value in relation_types_json.items()
        ]

        schema = DocREDSchema(relation_types=relation_types)
        with open(schema_path, "x") as f:
            f.write(schema.model_dump_json())
        return schema


def load_docred_units(
        split: Union[DocREDSplit, str],
) -> Iterable[DocREDUnit]:
    split = DocREDSplit(split)

    BASE_DOCRED_DIR = get_cache_dir(subpath="docred")
    GDRIVE_ID_BY_SPLIT: Mapping[DocREDSplit, str] = {
        DocREDSplit.TRAIN_ANNOTATED: "1NN33RzyETbanw4Dg2sRrhckhWpzuBQS9",
        DocREDSplit.TRAIN_DISTANT: "1Qr4Jct2IJ9BVI86_mCk_Pz0J32ww9dYw",
        DocREDSplit.DEV: "1AHUm1-_V9GCtGuDcc8XrMUCJE8B-HHoL",
        DocREDSplit.TEST: "1lAVDcD94Sigx7gR3jTfStI66o86cflum",
    }

    split_path = os.path.join(BASE_DOCRED_DIR, f"{split}.jsonl")

    if os.path.exists(split_path):
        with open(split_path, "r") as f:
            for line in f:
                unit = DocREDUnit.model_validate_json(line, strict=True)
                assert unit.is_labelled == (split != "test")
                yield unit

    else:
        units: list[DocREDUnit] = []

        raw_path = os.path.join(BASE_DOCRED_DIR, f"raw/{split}.json")
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        if not os.path.exists(raw_path):
            import gdown
            gdown.download(id=GDRIVE_ID_BY_SPLIT[split], output=raw_path)
        with open(raw_path, "r") as f:
            units_json = json.load(f)
            assert isinstance(units_json, list)

        for unit_json in units_json:
            assert isinstance(unit_json, dict)
            unit_json["vertex_set"] = unit_json.pop("vertexSet") # snake case
            unit = DocREDUnit.model_validate(unit_json, strict=False)
            assert unit.is_labelled == (split != "test")
            units.append(unit)

        del units_json # save some memory

        with open(split_path, "x") as f:
            for unit in units:
                f.write(unit.model_dump_json() + "\n")

        yield from units


__all__ = [
    "DocREDSplit",
    "load_docred_schema",
    "load_docred_units",
]

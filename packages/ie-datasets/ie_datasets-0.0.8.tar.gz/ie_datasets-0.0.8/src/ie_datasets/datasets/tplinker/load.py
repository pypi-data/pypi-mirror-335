from enum import StrEnum
import json
import os
import shutil
from typing import Iterable, Mapping, Union

import gdown

from ie_datasets.datasets.tplinker.schema import TPLinkerRelationType, TPLinkerSchema
from ie_datasets.datasets.tplinker.unit import TPLinkerUnit
from ie_datasets.util.decompress import decompress_tar_gz
from ie_datasets.util.env import get_cache_dir


class TPLinkerDatasetName(StrEnum):
    NYT = "NYT"
    NYT_STAR = "NYT*"
    WEBNLG = "WebNLG"
    WEBNLG_STAR = "WebNLG*"


class TPLinkerSplit(StrEnum):
    TRAIN = "train"
    VALID = "valid"
    TEST = "test"


FILENAMES_BY_DATASET_AND_SPLIT: Mapping[TPLinkerDatasetName, tuple[str, Mapping[TPLinkerSplit, str]]] = {
    TPLinkerDatasetName.NYT: ("nyt", {
        TPLinkerSplit.TRAIN: "train_data.json",
        TPLinkerSplit.VALID: "valid_data.json",
        TPLinkerSplit.TEST: "test_data.json",
    }),
    TPLinkerDatasetName.NYT_STAR: ("nyt_star", {
        TPLinkerSplit.TRAIN: "train_data.json",
        TPLinkerSplit.VALID: "valid_data.json",
        TPLinkerSplit.TEST: "test_triples.json",
    }),
    TPLinkerDatasetName.WEBNLG: ("webnlg", {
        TPLinkerSplit.TRAIN: "train_data.json",
        TPLinkerSplit.VALID: "valid_data.json",
        TPLinkerSplit.TEST: "test.json",
    }),
    TPLinkerDatasetName.WEBNLG_STAR: ("webnlg_star", {
        TPLinkerSplit.TRAIN: "train_data.json",
        TPLinkerSplit.VALID: "valid_data.json",
        TPLinkerSplit.TEST: "test_triples.json",
    }),
}


def _download():
    BASE_TPLINKER_DIR = get_cache_dir(subpath="tplinker")
    data_path = os.path.join(BASE_TPLINKER_DIR, "data4tplinker/data4bert")
    if not os.path.exists(data_path):
        GDRIVE_ID = "1RxBVMSTgBxhGyhaPEWPdtdX1aOmrUPBZ"

        tar_gz_path = os.path.join(BASE_TPLINKER_DIR, "tplinker.tar.gz")
        gdown.download(id=GDRIVE_ID, output=tar_gz_path)
        decompress_tar_gz(tar_gz_path, BASE_TPLINKER_DIR)
        os.remove(tar_gz_path)
        shutil.rmtree(os.path.join(BASE_TPLINKER_DIR, "data4tplinker/data4bilstm"))
    return data_path


def load_tplinker_schema(
        dataset: Union[TPLinkerDatasetName, str],
) -> TPLinkerSchema:
    dataset = TPLinkerDatasetName(dataset)

    data_path = _download()
    dataset_dir, _ = FILENAMES_BY_DATASET_AND_SPLIT[dataset]

    with open(os.path.join(data_path, dataset_dir, "rel2id.json"), "r") as f:
        relation_to_id = json.load(f)
    assert isinstance(relation_to_id, dict)

    schema = TPLinkerSchema(relation_types=[
        TPLinkerRelationType(id=id, name=name)
        for name, id in relation_to_id.items()
    ])
    return schema


def load_tplinker_units(
        dataset: Union[TPLinkerDatasetName, str],
        split: Union[TPLinkerSplit, str],
) -> Iterable[TPLinkerUnit]:
    dataset = TPLinkerDatasetName(dataset)
    split = TPLinkerSplit(split)

    schema = load_tplinker_schema(dataset)

    data_path = _download()
    dataset_dir, filenames_by_split = FILENAMES_BY_DATASET_AND_SPLIT[dataset]
    filename = filenames_by_split[split]

    with open(os.path.join(data_path, dataset_dir, filename), "r") as f:
        units_json = json.load(f)

    for unit_json in units_json:
        unit = TPLinkerUnit.model_validate(unit_json)
        schema.validate_unit(unit)
        yield unit


__all__ = [
    "load_tplinker_schema",
    "load_tplinker_units",
    "TPLinkerDatasetName",
    "TPLinkerSplit",
]

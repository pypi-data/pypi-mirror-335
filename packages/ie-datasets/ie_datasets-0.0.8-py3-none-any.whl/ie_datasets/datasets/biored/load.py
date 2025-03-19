from enum import StrEnum
import json
import os
from typing import Iterable, Union

from ie_datasets.datasets.biored.unit import BioREDUnit
from ie_datasets.util.decompress import decompress_zip
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import wget


class BioREDSplit(StrEnum):
    TRAIN = "Train"
    DEV = "Dev"
    TEST = "Test"


def _download() -> str:
    BASE_CUAD_DIR = get_cache_dir(subpath="biored")

    data_dir = os.path.join(BASE_CUAD_DIR, "BioRED")
    if not os.path.exists(data_dir):
        DATA_URL = "https://ftp.ncbi.nlm.nih.gov/pub/lu/BioRED/BIORED.zip"
        zip_path = os.path.join(BASE_CUAD_DIR, "BIORED.zip")
        wget(url=DATA_URL, local_path=zip_path)
        decompress_zip(zip_path, BASE_CUAD_DIR)
        os.remove(zip_path)
    return data_dir


def load_biored_units(split: Union[BioREDSplit, str]) -> Iterable[BioREDUnit]:
    split = BioREDSplit(split)

    data_dir = _download()
    split_path = os.path.join(data_dir, f"{split}.BioC.JSON")
    with open(split_path, "r") as f:
        data = json.load(f)
    assert data["source"] == "PubTator"
    assert data["date"] == "2021-11-30"
    assert data["key"] == "BioC.key"

    documents = data["documents"]
    for document in documents:
        unit = BioREDUnit.model_validate(document)
        yield unit


__all__ = [
    "BioREDSplit",
    "load_biored_units",
]

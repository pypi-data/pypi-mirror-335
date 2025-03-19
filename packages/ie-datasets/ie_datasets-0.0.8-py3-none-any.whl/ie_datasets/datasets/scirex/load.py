from enum import StrEnum
import os
from typing import Iterable, Union

from ie_datasets.datasets.scirex.unit import SciREXUnit
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.decompress import decompress_tar_gz
from ie_datasets.util.wget import wget


class SciREXSplit(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


def load_scirex_units(
        split: Union[SciREXSplit, str],
) -> Iterable[SciREXUnit]:
    BASE_SCIREX_DIR = get_cache_dir(subpath="scirex")

    split = SciREXSplit(split)

    split_path = os.path.join(BASE_SCIREX_DIR, f"release_data/{split}.jsonl")

    if not os.path.exists(split_path):
        DATA_URL = "https://raw.githubusercontent.com/allenai/SciREX/refs/heads/master/scirex_dataset/release_data.tar.gz"

        tar_gz_path = os.path.join(BASE_SCIREX_DIR, "data.tar.gz")
        wget(url=DATA_URL, local_path=tar_gz_path)
        decompress_tar_gz(tar_gz_path, out_dir=BASE_SCIREX_DIR)

        os.remove(tar_gz_path)

    with open(split_path, "r") as f:
        for line in f:
            unit = SciREXUnit.model_validate_json(line)
            yield unit


__all__ = [
    "load_scirex_units",
    "SciREXSplit",
]

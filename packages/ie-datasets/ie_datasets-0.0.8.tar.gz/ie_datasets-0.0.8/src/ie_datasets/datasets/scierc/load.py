from enum import StrEnum
import json
import os
import shutil
from typing import Iterable, Union

from ie_datasets.datasets.scierc.unit import SciERCUnit
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import wget
from ie_datasets.util.decompress import decompress_tar_gz


class SciERCSplit(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


def _download_scierc() -> str:
    BASE_SCIERC_DIR = get_cache_dir(subpath="scierc")

    json_dir = os.path.join(BASE_SCIERC_DIR, "processed_data/json")
    if not os.path.exists(json_dir):
        DATA_URL = "http://nlp.cs.washington.edu/sciIE/data/sciERC_processed.tar.gz"

        tar_gz_path = os.path.join(BASE_SCIERC_DIR, "scierc.tar.gz")
        wget(url=DATA_URL, local_path=tar_gz_path)
        decompress_tar_gz(tar_gz_path=tar_gz_path, out_dir=BASE_SCIERC_DIR)
        # drop unneeded files
        shutil.rmtree(tar_gz_path)
        shutil.rmtree(os.path.join(BASE_SCIERC_DIR, "processed_data/elmo"))
    return json_dir


def load_scierc_units(
        split: Union[SciERCSplit, str],
) -> Iterable[SciERCUnit]:
    BASE_SCIERC_DIR = get_cache_dir(subpath="scierc")

    split = SciERCSplit(split)

    split_path = os.path.join(BASE_SCIERC_DIR, f"{split}.jsonl")

    if os.path.exists(split_path):
        with open(split_path, "r") as f:
            for line in f:
                yield SciERCUnit.model_validate_json(line, strict=True)

    else:
        json_dir = _download_scierc()

        raw_split_path = os.path.join(json_dir, f"{split}.json")
        with open(raw_split_path, "r") as f:
            units: list[SciERCUnit] = []
            for i, line in enumerate(f):
                if i == 282:
                    unit_json = json.loads(line)
                    assert unit_json["doc_key"] == "H05-1117"
                    cluster = unit_json["clusters"][0]
                    assert cluster[2] == cluster[3] == [106, 106]
                    cluster.pop(3)
                    line = json.dumps(unit_json)
                unit = SciERCUnit.model_validate_json(line, strict=True)
                units.append(unit)

        with open(split_path, "x") as f:
            for unit in units:
                f.write(unit.model_dump_json() + "\n")

        yield from units


__all__ = [
    "load_scierc_units",
    "SciERCSplit",
]

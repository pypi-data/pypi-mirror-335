import json
import os
from typing import Iterable

from ie_datasets.datasets.cuad.unit import CUADUnit
from ie_datasets.util.decompress import decompress_zip
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import wget


def load_cuad_units() -> Iterable[CUADUnit]:
    BASE_CUAD_DIR = get_cache_dir(subpath="cuad")
    DATA_URL = "https://zenodo.org/records/4595826/files/CUAD_v1.zip"

    json_path = os.path.join(BASE_CUAD_DIR, "CUAD_v1/CUAD_v1.json")
    if not os.path.exists(json_path):
        zip_path = os.path.join(BASE_CUAD_DIR, "CUAD_v1.zip")
        wget(url=DATA_URL, local_path=zip_path)
        decompress_zip(zip_path, BASE_CUAD_DIR)
        os.remove(zip_path)

    with open(json_path, "r") as f:
        data = json.load(f)
    assert data["version"] == "aok_v1.0"

    units_json = data["data"]
    assert isinstance(units_json, list)
    assert len(units_json) == 510

    for unit_json in units_json:
        unit = CUADUnit.model_validate(unit_json)
        yield unit


__all__ = [
    "load_cuad_units",
]

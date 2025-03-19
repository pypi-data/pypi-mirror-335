from enum import StrEnum
from typing import Iterable, Union

from datasets import load_dataset

from ie_datasets.datasets.hyperred.unit import HyperREDUnit
from ie_datasets.util.env import get_cache_dir


class HyperREDSplit(StrEnum):
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


def load_hyperred_units(
        split: Union[HyperREDSplit, str],
) -> Iterable[HyperREDUnit]:
    BASE_HYPERRED_DIR = get_cache_dir(subpath="hyperred")

    split = HyperREDSplit(split)

    dataset = load_dataset(
        path="declare-lab/HyperRED",
        split=split,
        cache_dir=BASE_HYPERRED_DIR,
    )
    for raw_unit in dataset:
        # strict mode causes an error when reading spans as tuples
        unit = HyperREDUnit.model_validate(raw_unit, strict=False)
        yield unit


__all__ = [
    "HyperREDSplit",
    "load_hyperred_units",
]

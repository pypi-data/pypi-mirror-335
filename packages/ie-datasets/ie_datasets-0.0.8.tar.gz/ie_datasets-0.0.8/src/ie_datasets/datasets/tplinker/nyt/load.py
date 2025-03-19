from typing import Iterable, Union

from ie_datasets.datasets.tplinker.schema import TPLinkerSchema
from ie_datasets.datasets.tplinker.unit import TPLinkerUnit
from ie_datasets.datasets.tplinker.load import (
    load_tplinker_schema,
    load_tplinker_units,
    TPLinkerDatasetName,
    TPLinkerSplit,
)


def load_tplinker_nyt_schema() -> TPLinkerSchema:
    return load_tplinker_schema(
        dataset=TPLinkerDatasetName.NYT,
    )


def load_tplinker_nyt_units(
        split: Union[TPLinkerSplit, str],
) -> Iterable[TPLinkerUnit]:
    yield from load_tplinker_units(
        dataset=TPLinkerDatasetName.NYT,
        split=split,
    )


__all__ = [
    "load_tplinker_nyt_schema",
    "load_tplinker_nyt_units",
]

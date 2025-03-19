from enum import StrEnum
import os
from typing import Iterable, Union

from ie_datasets.datasets.chemprot.unit import (
    ChemProtEntityMention,
    ChemProtRelation,
    ChemProtUnit,
)
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import wget


class ChemProtSplit(StrEnum):
    SAMPLE = "sample"
    TRAIN = "train"
    VALIDATION = "validation"
    TEST = "test"


def load_chemprot_units(
        split: Union[ChemProtSplit, str],
) -> Iterable[ChemProtUnit]:
    split = ChemProtSplit(split)

    BASE_CHEMPROT_DIR = get_cache_dir(subpath="chemprot")
    BASE_DATA_URL = "https://huggingface.co/datasets/bigbio/chemprot/resolve/refs%2Fconvert%2Fparquet/chemprot_full_source"

    split_url = f"{BASE_DATA_URL}/{split}/0000.parquet"
    split_path = os.path.join(BASE_CHEMPROT_DIR, f"{split}.parquet")
    wget(split_url, split_path)

    from pandas import DataFrame
    import pyarrow.parquet as pq

    table = pq.read_table(split_path)
    df = table.to_pandas()
    assert isinstance(df, DataFrame)

    for i, row in df.iterrows():
        e = row["entities"]
        entities = [
            ChemProtEntityMention(
                id=id,
                entity_type=t,
                text=text,
                start=start,
                end=end,
            )
            for id, t, text, (start, end)
            in zip(e["id"], e["type"], e["text"], e["offsets"], strict=True)
        ]

        r = row["relations"]
        relations = [
            ChemProtRelation(
                relation_type=t,
                argument_1=arg1,
                argument_2=arg2,
            )
            for t, arg1, arg2
            in zip(r["type"], r["arg1"], r["arg2"])
        ]

        unit = ChemProtUnit(
            pmid=int(row["pmid"]),
            text=row["text"],
            entities=entities,
            relations=relations,
        )
        yield unit


__all__ = [
    "ChemProtSplit",
    "load_chemprot_units",
]

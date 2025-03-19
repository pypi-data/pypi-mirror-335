from enum import StrEnum
import os
from typing import Iterable, Union

from ie_datasets.datasets.knowledgenet.unit import KnowledgeNetUnit
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import open_or_wget


class KnowledgeNetSplit(StrEnum):
    TRAIN = "train"
    TEST = "test-no-facts"


def load_knowledgenet_units(
        split: Union[KnowledgeNetSplit, str],
) -> Iterable[KnowledgeNetUnit]:
    BASE_CROSSRE_PATH = get_cache_dir(subpath="crossre")
    BASE_DATA_URL = "https://raw.githubusercontent.com/diffbot/knowledge-net/refs/heads/master/dataset"

    split = KnowledgeNetSplit(split)

    split_path = os.path.join(BASE_CROSSRE_PATH, f"{split}.jsonl")
    data_url = f"{BASE_DATA_URL}/{split}.json"
    with open_or_wget(split_path, data_url) as f:
        for line in f:
            unit = KnowledgeNetUnit.model_validate_json(line)
            if split is KnowledgeNetSplit.TEST:
                assert unit.num_facts == 0
            yield unit


__all__ = [
    "load_knowledgenet_units",
    "KnowledgeNetSplit",
]

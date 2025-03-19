from enum import StrEnum
import os
from typing import Iterable, Union

from ie_datasets.datasets.crossre.unit import CrossREUnit
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import open_or_wget


class CrossREDomain(StrEnum):
    AI = "ai"
    LITERATURE = "literature"
    MUSIC = "music"
    NEWS = "news"
    NEWS_2 = "news-2"
    POLITICS = "politics"
    SCIENCE = "science"

class CrossRESplit(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


def load_crossre_units(
        split: Union[CrossRESplit, str],
        *,
        domain: Union[CrossREDomain, str],
) -> Iterable[CrossREUnit]:
    split = CrossRESplit(split)
    domain = CrossREDomain(domain)

    BASE_CROSSRE_PATH = get_cache_dir(subpath="crossre")
    BASE_DATA_URL = "https://raw.githubusercontent.com/mainlp/CrossRE/refs/heads/main"

    if domain is CrossREDomain.NEWS_2:
        data_url = f"{BASE_DATA_URL}/crossre_extension/news-{split}.json"
    else:
        data_url = f"{BASE_DATA_URL}/crossre_data/{domain}-{split}.json"

    split_path = os.path.join(BASE_CROSSRE_PATH, f"{domain}-{split}.jsonl")
    with open_or_wget(split_path, data_url) as f:
        for line in f:
            unit = CrossREUnit.model_validate_json(line)
            yield unit


__all__ = [
    "CrossREDomain",
    "CrossRESplit",
    "load_crossre_units",
]

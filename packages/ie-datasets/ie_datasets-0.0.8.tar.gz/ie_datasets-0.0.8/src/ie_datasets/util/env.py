import os
from typing import Optional

from platformdirs import user_data_dir


def get_env(key: str, default: Optional[str] = None) -> str:
    if default is None:
        return os.environ[key]
    else:
        return os.environ.get(key, default=default)


BASE_CACHE_DIR = get_env(
    key="IE_DATASETS_CACHE_DIR",
    default=user_data_dir(appname="ie_datasets"),
)

def get_cache_dir(
        subpath: Optional[str] = None,
        base_cache_dir: str = BASE_CACHE_DIR,
) -> str:
    path = base_cache_dir
    if subpath is not None:
        path = os.path.join(path, subpath)
    os.makedirs(path, exist_ok=True)
    return path

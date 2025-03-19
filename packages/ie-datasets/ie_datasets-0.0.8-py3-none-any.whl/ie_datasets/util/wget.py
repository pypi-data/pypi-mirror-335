from contextlib import contextmanager
from io import TextIOWrapper
import os
from urllib import request
from typing import Iterator, Optional


def wget(
        url: str,
        local_path: str,
        clobber: bool = False,
) -> None:
    local_dir = os.path.dirname(local_path)
    if local_dir != "":
        os.makedirs(local_dir, exist_ok=True)

    if os.path.exists(local_path):
        assert os.path.isfile(local_path)
        if clobber:
            print(f"Clobbering file at {local_path}")
            os.remove(local_path)
        else:
            return

    print(f"Downloading {url} as {local_path}")
    request.urlretrieve(url, filename=local_path)


@contextmanager
def open_or_wget(
        local_path: str,
        url: str,
        clobber: bool = False,
        encoding: Optional[str] = None,
) -> Iterator[TextIOWrapper]:
    wget(url=url, local_path=local_path, clobber=clobber)
    with open(local_path, mode="r", encoding=encoding) as f:
        yield f

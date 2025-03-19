"""
Adapted from dave-s477/SoMeNLP/bin/split_data
"""
from enum import StrEnum
import os
import random
import shutil

from math import ceil


class SoMeSciSplit(StrEnum):
    TRAIN = "train"
    DEVEL = "devel"
    TEST = "test"


def somesci_split(
        in_path: str,
        *,
        file_extension: str = ".txt",
        train_ratio: int = 60,
        devel_ratio: int = 20,
        test_ratio: int = 20,
        seed: int = 2,
        move: bool = True,
):
    """
    Split corpus according to a specified ratio.
    in_path: Path to input dir. Subdirectories for each split will be created here.
    file_extension: Extension for recognizing unique files.
    seed: The seed for random shuffling (default of 2 is hard-coded in SoMeSci)
    move: Move files instead of copying them (more efficient)
    """
    in_path = in_path.rstrip('/')

    assert train_ratio >= 0
    assert devel_ratio >= 0
    assert test_ratio >= 0
    if train_ratio + devel_ratio + test_ratio != 100:
        raise RuntimeError(f"Input ratios do not sum to 100")

    # glob is absurdly slow so we use listdir instead
    in_path_files = os.listdir(in_path)
    single_filenames = [f for f in in_path_files if f.endswith(file_extension)]
    all_files: list[list[str]] = []
    for filename in single_filenames:
        base_file_name = filename.removesuffix(file_extension)
        base_file_entries = [f for f in in_path_files if f.startswith(base_file_name)]
        all_files.append(base_file_entries)

    rng = random.Random(seed)
    rng.shuffle(all_files)

    cut_sum = 0
    prev_cut_idx = 0
    for cut, split_name in [
        (train_ratio, SoMeSciSplit.TRAIN),
        (devel_ratio, SoMeSciSplit.DEVEL),
        (test_ratio, SoMeSciSplit.TEST),
    ]:
        cut_sum += cut
        cut_idx = ceil(len(all_files) * cut_sum / 100.0)
        split_path = os.path.join(in_path, split_name)
        os.makedirs(split_path, exist_ok=True)
        for files in all_files[prev_cut_idx:cut_idx]:
            for f in files:
                source_path = os.path.join(in_path, f)
                target_path = os.path.join(split_path, f)
                if move:
                    shutil.move(source_path, target_path)
                else:
                    shutil.copy(source_path, target_path)
        prev_cut_idx = cut_idx


__all__ = [
    "somesci_split",
    "SoMeSciSplit",
]

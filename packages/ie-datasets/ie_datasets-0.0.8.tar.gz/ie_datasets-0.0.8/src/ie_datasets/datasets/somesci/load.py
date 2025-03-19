from enum import StrEnum
import os
import re
from typing import Iterable, Optional, Mapping, Union

from pybrat.parser import BratParser

from ie_datasets.datasets.somesci.schema import (
    SoMeSciEntityType,
    SoMeSciRelationType,
    SoMeSciSchema,
)
from ie_datasets.datasets.somesci.split import somesci_split, SoMeSciSplit
from ie_datasets.datasets.somesci.unit import SoMeSciUnit
from ie_datasets.util.decompress import decompress_zip
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import wget


class SoMeSciVersion(StrEnum):
    V0_1 = "0.1"
    V0_2 = "0.2"
    V1_1 = "1.1"

DEFAULT_SOMESCI_VERSION = SoMeSciVersion.V1_1


class SoMeSciGroup(StrEnum):
    CREATION_SENTENCES = "Creation_sentences"
    PUBLIC_LIBRARY_OF_SCIENCE_METHODS = "PLoS_methods"
    PUBLIC_LIBRARY_OF_SCIENCE_SENTENCES = "PLoS_sentences"
    PUBMED_FULLTEXT = "Pubmed_fulltext"


def _download_somesci_version(
        version: Optional[Union[SoMeSciVersion, str]] = None,
) -> str:
    BASE_SOMESCI_DIR = get_cache_dir(subpath="somesci")

    if version is None:
        version = DEFAULT_SOMESCI_VERSION
    else:
        version = SoMeSciVersion(version)

    version_dir = os.path.join(BASE_SOMESCI_DIR, version.replace('.','_'))
    labels_dir_name = "SoMeSci/Labels" if version == "0.1" else "SoMeSci/Label"
    label_dir = os.path.join(version_dir, labels_dir_name)

    if not os.path.exists(label_dir):
        DATA_URL_BY_VERSION: Mapping[SoMeSciVersion, str] = {
            SoMeSciVersion.V0_1: "https://zenodo.org/records/4701764/files/SoMeSci.zip",
            SoMeSciVersion.V0_2: "https://zenodo.org/records/4968738/files/SoMeSci.zip",
            SoMeSciVersion.V1_1: "https://zenodo.org/records/8100213/files/SoMeSci.zip",
        }
        data_url = DATA_URL_BY_VERSION[version]
        zip_path = os.path.join(version_dir, "SoMeSci.zip")
        wget(url=data_url, local_path=zip_path)
        decompress_zip(zip_path=zip_path, out_dir=version_dir)

    return label_dir


def load_somesci_schema(
        version: Optional[Union[SoMeSciVersion, str]] = None,
) -> SoMeSciSchema:
    """
    Load the schema for the SoMeSci dataset.
    Versions 0.1, 0.2, and 1.1 all share the same schema.
    """
    RELATION_REGEX = re.compile(r"^(?P<relation>[A-Za-z]+(_[A-Za-z]+)*)\s+Arg1:(?P<argument_1>[A-Za-z]+(_[A-Za-z]+)*(\|([A-Za-z]+(_[A-Za-z]+)*))*), Arg2:(?P<argument_2>[A-Za-z]+(_[A-Za-z]+)*(\|([A-Za-z]+(_[A-Za-z]+)*))*)$")

    label_dir = _download_somesci_version(version)
    conf_path = os.path.join(label_dir, "conf/annotation.conf")

    with open(conf_path, "r") as f:
        lines = [line.strip() for line in f.readlines()]
    lines = [line for line in lines if len(line) > 0] # remove empty lines

    entities_index = lines.index("[entities]")
    events_index = lines.index("[events]")
    relations_index = lines.index("[relations]")
    attributes_index = lines.index("[attributes]")
    assert 0 < entities_index < events_index < relations_index < attributes_index

    entity_lines = lines[entities_index+1:events_index]
    relation_lines = lines[relations_index+1:attributes_index]

    entity_types = [
        SoMeSciEntityType(name=line)
        for line in entity_lines
    ]

    relation_types = []
    for i, line in enumerate(relation_lines):
        match = RELATION_REGEX.match(line)
        assert match is not None
        assert match.span() == (0, len(line))
        match_dict = match.groupdict()

        relation_name = match_dict["relation"]
        assert isinstance(relation_name, str)
        argument_1_types = match_dict["argument_1"].split("|")
        argument_2_types = match_dict["argument_2"].split("|")

        # fix error #1
        if i == 5:
            assert relation_name == "Abbreviation_of"
            assert argument_1_types[0] == "abbreviation"
            argument_1_types[0] = "Abbreviation"

        relation_types.append(SoMeSciRelationType(
            name=relation_name,
            argument_1_types=argument_1_types,
            argument_2_types=argument_2_types,
        ))

    return SoMeSciSchema(
        entity_types=entity_types,
        relation_types=relation_types,
    )


def load_somesci_units(
        split: Union[SoMeSciSplit, str],
        *,
        version: Optional[Union[SoMeSciVersion, str]] = None,
        group: Union[SoMeSciGroup, str],
) -> Iterable[SoMeSciUnit]:
    schema = load_somesci_schema(version=version)

    split = SoMeSciSplit(split)
    group = SoMeSciGroup(group)

    label_dir = _download_somesci_version(version)
    group_dir = os.path.join(label_dir, group)
    if not all(
        os.path.exists(os.path.join(group_dir, split))
        for split in ("train", "devel", "test")
    ):
        somesci_split(group_dir)

    split_dir = os.path.join(group_dir, split)

    parser = BratParser()
    units = parser.parse(split_dir)
    for unit in units:
        unit = SoMeSciUnit.from_brat(unit)
        schema.validate_unit(unit)
        yield unit


__all__ = [
    "load_somesci_schema",
    "load_somesci_units",
    "SoMeSciGroup",
    "SoMeSciVersion",
]

from enum import StrEnum
import glob
import os
import traceback
from typing import Iterable, Mapping, Optional, TypeAlias, Union

from pydantic import ValidationError

from ie_datasets.datasets.deft.unit import (
    DEFTEntity,
    DEFTEntityType,
    DEFTRelation,
    DEFTRelationType,
    DEFTUnit,
)
from ie_datasets.util.decompress import decompress_zip
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.eprint import eprint
from ie_datasets.util.wget import wget


class DEFTSplit(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"

class DEFTCategory(StrEnum):
    BIOLOGY = "biology"
    HISTORY = "history"
    PHYSICS = "physics"
    PSYCHOLOGY = "psychology"
    ECONOMIC = "economic"
    SOCIOLOGY = "sociology"
    GOVERNMENT = "government"


DEFTRelationTag: TypeAlias = tuple[str, DEFTRelationType]
DEFTEntityTag: TypeAlias = tuple[bool, DEFTEntityType, str]


def _parse_deft_line(line: str) -> tuple[
    str,
    str,
    int,
    int,
    Optional[tuple[DEFTEntityTag, Optional[DEFTRelationTag]]],
]:
    text, source, start, end, tag, id, root, relation_type = line.split("\t ")
    start = int(start)
    end = int(end)
    if tag == "O":
        assert id == "-1"
        assert root == "-1"
        return text, source, start, end, None

    BI, entity_type = tag.split("-", maxsplit=1)
    if BI == "B":
        is_begin = True
    else:
        is_begin = False
        assert BI == "I"
    entity_type = DEFTEntityType(entity_type)
    assert id != "-1"
    entity_tag = (is_begin, entity_type, id)

    assert root != "-1"
    if relation_type == "0":
        assert root == "0" or root == id
        return text, source, start, end, (entity_tag, None)
    else:
        relation_type = DEFTRelationType(relation_type)
        assert root != "0"
        relation_tag = (root, relation_type)
        return text, source, start, end, (entity_tag, relation_tag)


def _read_deft(filename: str) -> Iterable[DEFTUnit]:
    with open(filename, "r") as f:
        lines = f.readlines()

    # Fix error 1
    if filename.endswith("data/deft_files/train/t5_economic_1_202.deft"):
        assert lines.pop(2307) == "\n"
    # Fix error 2
    if filename.endswith("data/deft_files/dev/t4_psychology_1_0.deft"):
        assert lines.pop(168) == "\n"
    chunks = "".join(lines).strip("\n").split("\n\n\n")

    for chunk in chunks:
        try:
            sentences = [subchunk.split("\n") for subchunk in chunk.split("\n\n")]

            # manually split the ID if it is attached to the first sentence
            if len(sentences[0]) > 2:
                sentences = [sentences[0][:2], sentences[0][2:]] + sentences[1:]
            id_line, dot_line = sentences[0]

            id_str, source, id_start, id_end, tag = _parse_deft_line(id_line)
            assert tag is None
            assert _parse_deft_line(dot_line) == (".", source, id_end, id_end+1, None)
            id = int(id_str)
        except Exception as e:
            eprint(f"Error parsing chunk in file {filename}:\n{chunk}")
            raise

        """
        # Fix error 3
        if id == 56:
            assert source == "data/source_txt/t1_biology_0_0.deft"
            header = sentences.pop(1)
            assert len(header) == 1
            assert sentences[1][0] == "Isotopes\t data/source_txt/t1_biology_0_0.deft\t 5803\t 5811\t I-Term\t T181\t 0\t 0"
            sentences[1][0] = "Isotopes\t data/source_txt/t1_biology_0_0.deft\t 5803\t 5811\t B-Term\t T181\t 0\t 0"

        # Fix error 4
        elif id == 74: # 4.1
            assert source == "data/source_txt/t1_biology_0_0.deft"
            assert sentences[3][6] == "a\t data/source_txt/t1_biology_0_0.deft\t 8550\t 8551\t B-Referential-Definition\t T194\t T195\t Indirect-Defines"
            sentences[3][6] = "a\t data/source_txt/t1_biology_0_0.deft\t 8485\t 8486\t B-Referential-Definition\t T194\t T195\t Indirect-Defines"
        elif id == 263: # 4.2
            assert source == "data/source_txt/t1_biology_0_0.deft"
            assert sentences[3][7] == "inhibition\t data/source_txt/t1_biology_0_0.deft\t 30014\t 30024\t I-Referential-Definition\t T102\t T101\t Indirect-Defines"
            sentences[3][7] = "inhibition\t data/source_txt/t1_biology_0_0.deft\t 30046\t 30056\t I-Term\t T101\t 0\t 0"
        elif id == 266: # 4.3
            assert source == "data/source_txt/t1_biology_0_0.deft"
            assert sentences[3][16] == sentences[3][20] == "reactions\t data/source_txt/t1_biology_0_0.deft\t 30442\t 30451\t I-Referential-Definition\t T250\t T104\t Indirect-Defines"
            sentences[3][16] = "reactions\t data/source_txt/t1_biology_0_0.deft\t 30483\t 30492\t I-Term\t T104\t 0\t 0"
            sentences[3][20] = "reactions\t data/source_txt/t1_biology_0_0.deft\t 30503\t 30512\t I-Alias-Term\t T106\t T104\t AKA"
        elif id == 269: # 4.4
            assert source == "data/source_txt/t1_biology_0_0.deft"
            assert sentences[3][11] == "phosphorylation\t data/source_txt/t1_biology_0_0.deft\t 30783\t 30798\t I-Referential-Definition\t T108\t T107\t Indirect-Defines"
            sentences[3][11] = "phosphorylation\t data/source_txt/t1_biology_0_0.deft\t 30825\t 30840\t I-Term\t T107\t 0\t 0"
        """

        try:
            relations: set[DEFTRelation] = set()
            span_to_sentence_data: dict[
                tuple[int, int],
                tuple[str, list[tuple[DEFTEntityType, str, int, int]]]
            ] = {}
            for sentence in sentences[1:]:
                sentence_entities: list[tuple[DEFTEntityType, str, int, int]] = []
                current_entity: Optional[tuple[DEFTEntityType, str, int, int]] = None
                _, _, sentence_start, _, _ = _parse_deft_line(sentence[0])
                _, _, _, sentence_end, _ = _parse_deft_line(sentence[-1])
                sentence_chars = [" " for _ in range(sentence_start, sentence_end)]
                for line in sentence:
                    token, _source, start, end, tag = _parse_deft_line(line)
                    assert _source == source
                    assert sentence_start <= start < end <= sentence_end
                    assert len(token) == end - start
                    s = start - sentence_start
                    e = end - sentence_start
                    assert (c == " " for c in sentence_chars[s:e])
                    sentence_chars[s:e] = token

                    if tag is None:
                        if current_entity is not None:
                            sentence_entities.append(current_entity)
                            current_entity = None
                    else:
                        (is_begin, entity_type, entity_id), relation_tag = tag
                        if is_begin:
                            if current_entity is not None:
                                sentence_entities.append(current_entity)
                            current_entity = (entity_type, entity_id, s, e)
                        else:
                            assert current_entity is not None
                            (
                                current_entity_type,
                                current_entity_id,
                                current_start,
                                current_end,
                            ) = current_entity
                            assert current_entity_type == entity_type
                            assert current_entity_id == entity_id
                            assert current_end <= s, line
                            current_entity = (entity_type, entity_id, current_start, e)

                        if relation_tag is not None:
                            root_id, relation_type = relation_tag
                            relations.add(DEFTRelation(
                                root_id=root_id,
                                child_id=entity_id,
                                relation_type=relation_type,
                            ))

                if current_entity is not None:
                    sentence_entities.append(current_entity)

                sentence_span = (sentence_start, sentence_end)
                sentence_text = "".join(sentence_chars)
                if sentence_span in span_to_sentence_data:
                    existing_sentence_text, existing_entities = span_to_sentence_data[sentence_span]
                    assert sentence_text == existing_sentence_text
                    existing_entities.extend(sentence_entities)
                else:
                    for ss, se in span_to_sentence_data.keys():
                        assert se <= sentence_start or sentence_end <= ss
                    span_to_sentence_data[sentence_span] = (sentence_text, sentence_entities)

            text_acc = ""
            entities: list[DEFTEntity] = []
            for (
                (sentence_start, sentence_end),
                (sentence_text, sentence_entities),
            ) in sorted(span_to_sentence_data.items()):
                if text_acc == "":
                    offset = 0
                    text_acc = sentence_text
                else:
                    offset = len(text_acc) + 1
                    text_acc += " " + sentence_text

                for entity_type, entity_id, start, end in sentence_entities:
                    s = start + offset
                    e = end + offset
                    entities.append(
                        DEFTEntity(
                            id=entity_id,
                            entity_type=entity_type,
                            text=text_acc[s:e],
                            start_char=s,
                            end_char=e,
                        )
                    )

            yield DEFTUnit(
                id=id,
                source=source,
                text=text_acc,
                entities=entities,
                relations=list(relations),
            )

        except (AssertionError, ValidationError) as e:
            eprint(f"Skipping unit {id} in file {filename} due to error {e}")
            traceback.print_exception(e)
            continue

        except Exception as e:
            eprint(f"Error on unit {id} in file {filename}")
            raise


def _download() -> str:
    BASE_DEFT_DIR = get_cache_dir(subpath="deft")
    COMMIT_HASH = "db8c95565c2e58d861537cb8cb4621c50b75cd13"
    REPOSITORY_ZIP_URL = f"https://github.com/adobe-research/deft_corpus/archive/{COMMIT_HASH}.zip"

    repo_dir = os.path.join(BASE_DEFT_DIR, f"deft_corpus-{COMMIT_HASH}")
    if not os.path.exists(repo_dir):
        zip_path = os.path.join(BASE_DEFT_DIR, "deft_corpus.zip")
        wget(url=REPOSITORY_ZIP_URL, local_path=zip_path)
        decompress_zip(zip_path=zip_path, out_dir=BASE_DEFT_DIR)
        os.remove(zip_path)
    return repo_dir


def load_deft_units(
        split: Union[DEFTSplit, str],
        *,
        category: Union[DEFTCategory, str],
) -> Iterable[DEFTUnit]:
    BASE_DEFT_DIR = get_cache_dir(subpath="deft")

    split = DEFTSplit(split)
    category = DEFTCategory(category)

    cache_path: str = os.path.join(BASE_DEFT_DIR, f"{split}_{category}.jsonl")
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            for line in f:
                yield DEFTUnit.model_validate_json(line, strict=True)
    else:
        GLOBS_BY_SPLIT_AND_PATTERN: Mapping[DEFTSplit, Mapping[DEFTCategory, str]] = {
            DEFTSplit.TRAIN: {
                DEFTCategory.BIOLOGY: "data/deft_files/train/t1_biology_*_*.deft",
                DEFTCategory.HISTORY: "data/deft_files/train/t2_history_*_*.deft",
                DEFTCategory.PHYSICS: "data/deft_files/train/t3_physics_*_*.deft",
                DEFTCategory.PSYCHOLOGY: "data/deft_files/train/t4_psychology_*_*.deft",
                DEFTCategory.ECONOMIC: "data/deft_files/train/t5_economic_*_*.deft",
                DEFTCategory.SOCIOLOGY: "data/deft_files/train/t6_sociology_*_*.deft",
                DEFTCategory.GOVERNMENT: "data/deft_files/train/t7_government_*_*.deft",
            },
            DEFTSplit.DEV: {
                DEFTCategory.BIOLOGY: "data/deft_files/dev/t1_biology_*_*.deft",
                DEFTCategory.HISTORY: "data/deft_files/dev/t2_history_*_*.deft",
                DEFTCategory.PHYSICS: "data/deft_files/dev/t3_physics_*_*.deft",
                DEFTCategory.PSYCHOLOGY: "data/deft_files/dev/t4_psychology_*_*.deft",
                DEFTCategory.ECONOMIC: "data/deft_files/dev/t5_economic_*_*.deft",
                DEFTCategory.SOCIOLOGY: "data/deft_files/dev/t6_sociology_*_*.deft",
                DEFTCategory.GOVERNMENT: "data/deft_files/dev/t7_government_*_*.deft",
            },
            DEFTSplit.TEST: {
                DEFTCategory.BIOLOGY: "data/test_files/labeled/subtask_3/task_3_t1_biology_*_*.deft",
                DEFTCategory.HISTORY: "data/test_files/labeled/subtask_3/task_3_t2_history_*_*.deft",
                DEFTCategory.PHYSICS: "data/test_files/labeled/subtask_3/task_3_t3_physics_*_*.deft",
                DEFTCategory.PSYCHOLOGY: "data/test_files/labeled/subtask_3/task_3_t4_psychology_*_*.deft",
                DEFTCategory.ECONOMIC: "data/test_files/labeled/subtask_3/task_3_t5_economic_*_*.deft",
                DEFTCategory.SOCIOLOGY: "data/test_files/labeled/subtask_3/task_3_t6_sociology_*_*.deft",
                DEFTCategory.GOVERNMENT: "data/test_files/labeled/subtask_3/task_3_t7_government_*_*.deft",
            },
        }

        repo_dir = _download()
        pattern = GLOBS_BY_SPLIT_AND_PATTERN[split][category]
        units_by_id: dict[int, DEFTUnit] = {}
        for filename in glob.glob(os.path.join(repo_dir, pattern)):
            for unit in _read_deft(filename):
                assert unit.id not in units_by_id
                units_by_id[unit.id] = unit
        units = [units_by_id[id] for id in sorted(units_by_id.keys())]

        with open(cache_path, "x") as f:
            for unit in units:
                f.write(unit.model_dump_json() + "\n")

        yield from units


__all__ = [
    "DEFTCategory",
    "DEFTSplit",
    "load_deft_units",
]

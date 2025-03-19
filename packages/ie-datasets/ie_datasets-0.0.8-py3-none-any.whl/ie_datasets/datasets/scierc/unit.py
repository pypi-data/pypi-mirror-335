from enum import StrEnum
from typing import Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class SciERCEntityType(StrEnum):
    GENERIC = "Generic"
    MATERIAL = "Material"
    METHOD = "Method"
    METRIC = "Metric"
    OTHER_SCIENTIFIC_TERM = "OtherScientificTerm"
    TASK = "Task"


class SciERCRelationType(StrEnum):
    COMPARE = "COMPARE"
    CONJUNCTION = "CONJUNCTION"
    EVALUATE_FOR = "EVALUATE-FOR"
    FEATURE_OF = "FEATURE-OF"
    HYPONYM_OF = "HYPONYM-OF"
    PART_OF = "PART-OF"
    USED_FOR = "USED-FOR"


class SciERCUnit(ImmutableModel):
    doc_key: str
    sentences: Sequence[Sequence[str]]
    clusters: Sequence[Sequence[tuple[int, int]]] # coreference resolution
    ner: Sequence[Sequence[tuple[int, int, SciERCEntityType]]]
    relations: Sequence[Sequence[tuple[int, int, int, int, SciERCRelationType]]]

    @model_validator(mode="after")
    def validate_clusters(self):
        for clusters in self.clusters:
            assert clusters == sorted(set(clusters))
        return self

    @model_validator(mode="after")
    def validate_sentences(self):
        assert len(self.sentences) == len(self.ner) == len(self.relations)
        return self

    @model_validator(mode="after")
    def validate_ner(self):
        for ner in self.ner:
            for start, end, entity_type in ner:
                assert start <= end
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relations in self.relations:
            for start1, end1, start2, end2, relation_type in relations:
                assert start1 <= end1
                assert start2 <= end2
        return self

    @property
    def num_tokens(self) -> int:
        return sum(len(sentence) for sentence in self.sentences)

    @property
    def num_sentences(self) -> int:
        return len(self.sentences)

    @property
    def num_entity_mentions(self) -> int:
        return sum(len(ner) for ner in self.ner)

    @property
    def num_relations(self) -> int:
        return sum(len(relations) for relations in self.relations)

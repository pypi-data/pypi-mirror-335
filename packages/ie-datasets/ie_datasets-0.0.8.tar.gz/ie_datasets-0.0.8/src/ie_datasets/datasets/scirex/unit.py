from enum import Enum
from functools import cached_property
from typing import Mapping, Sequence, Union

from ie_datasets.util.interfaces import ImmutableModel


class SciREXEntityType(str, Enum):
    METHOD = "Method"
    METRIC = "Metric"
    TASK = "Task"
    MATERIAL = "Material"


class SciREXRelation(ImmutableModel):
    Method: str
    Metric: str
    Task: str
    Material: str
    score: Union[str, float]


class SciREXUnit(ImmutableModel):
    doc_id: str
    words: Sequence[str]
    sentences: Sequence[tuple[int, int]]
    sections: Sequence[tuple[int, int]]
    ner: Sequence[tuple[int, int, SciREXEntityType]]
    coref: Mapping[str, Sequence[tuple[int, int]]]
    n_ary_relations: Sequence[SciREXRelation]
    method_subrelations: Mapping[str, list[tuple[tuple[int, int], str]]]

    @property
    def num_words(self) -> int:
        return len(self.words)

    @property
    def num_sentences(self) -> int:
        return len(self.sentences)

    @property
    def num_entity_mentions(self) -> int:
        return len(self.ner)

    @property
    def num_relations(self) -> int:
        return len(self.n_ary_relations)

    """
    From the README:
    A note of concern:
    Further analysis of our dataset revealed that ~50% of relations contain atleast one entity with no mentions in the paper (they occur in tables which we have discarded from our dataset).
    This makes evaluation of end to end task difficult (no predicted cluster can match that gold cluster).
    Currently, we remove these relations during evaluation for the end to end task (https://github.com/allenai/SciREX/blob/master/scirex/evaluation_scripts/scirex_relation_evaluate.py#L110).
    Note that this artifically reduces the precision of our model.

    We implement these checks below as the following properties.
    """

    @cached_property
    def grounded_entities(self) -> Mapping[str, Sequence[tuple[int, int]]]:
        return {
            entity_name: mentions
            for entity_name, mentions in self.coref.items()
            if len(mentions) > 0
        }

    @cached_property
    def grounded_relations(self) -> Sequence[SciREXRelation]:
        return [
            relation for relation in self.n_ary_relations
            if all(
                entity_name in self.grounded_entities
                for entity_name in (
                    relation.Method,
                    relation.Metric,
                    relation.Task,
                    relation.Material,
                )
            )
        ]


__all__ = [
    "SciREXEntityType",
    "SciREXRelation",
    "SciREXUnit",
]

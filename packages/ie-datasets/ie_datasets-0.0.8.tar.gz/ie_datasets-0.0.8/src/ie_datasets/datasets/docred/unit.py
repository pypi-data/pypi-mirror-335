from typing import Optional, Sequence

from pydantic import model_validator

from ie_datasets.datasets.docred.schema import (
    DocREDEntityTypeID,
    DocREDRelationTypeID,
)
from ie_datasets.util.interfaces import ImmutableModel


class DocREDEntityMention(ImmutableModel):
    name: str
    pos: tuple[int, int]
    sent_id: int
    type: DocREDEntityTypeID


class DocREDRelation(ImmutableModel):
    r: DocREDRelationTypeID
    h: int
    t: int
    evidence: Sequence[int]


class DocREDUnit(ImmutableModel):
    title: str
    sents: Sequence[Sequence[str]]
    vertex_set: Sequence[Sequence[DocREDEntityMention]]
    labels: Optional[Sequence[DocREDRelation]] = None

    @property
    def num_tokens(self) -> int:
        return sum(len(sent) for sent in self.sents)

    @property
    def num_sentences(self) -> int:
        return len(self.sents)

    @property
    def num_entities(self) -> int:
        return len(self.vertex_set)

    @property
    def num_relations(self) -> int:
        return 0 if self.labels is None else len(self.labels)

    @property
    def is_labelled(self) -> bool:
        return self.labels is not None

    @model_validator(mode="after")
    def validate_entities(self):
        for entity_mentions in self.vertex_set:
            assert len(entity_mentions) > 0
            for mention in entity_mentions:
                sentence = self.sents[mention.sent_id]
                start, end = mention.pos
                assert 0 <= start < end <= len(sentence)
        return self


__all__ = [
    "DocREDEntityMention",
    "DocREDRelation",
    "DocREDUnit",
]

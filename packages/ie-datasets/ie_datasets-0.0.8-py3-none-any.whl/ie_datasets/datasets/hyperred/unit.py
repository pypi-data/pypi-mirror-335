from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class HyperREDEntity(ImmutableModel):
    span: tuple[int, int]


class HyperREDQualifier(ImmutableModel):
    span: tuple[int, int]
    label: str


class HyperREDRelation(ImmutableModel):
    head: tuple[int, int]
    tail: tuple[int, int]
    label: str
    qualifiers: Sequence[HyperREDQualifier]


class HyperREDUnit(ImmutableModel):
    tokens: Sequence[str]
    entities: Sequence[HyperREDEntity]
    relations: Sequence[HyperREDRelation]

    @property
    def num_tokens(self) -> int:
        return len(self.tokens)

    @property
    def num_entities(self) -> int:
        return len(self.entities)

    @property
    def num_relations(self) -> int:
        return len(self.relations)

    @cached_property
    def entities_by_span(self) -> Mapping[tuple[int, int], HyperREDEntity]:
        entities_by_span = {entity.span: entity for entity in self.entities}
        assert len(entities_by_span) == self.num_entities, self
        return entities_by_span

    @model_validator(mode="after")
    def validate_spans(self):
        T = self.num_tokens
        for entity in self.entities:
            s, e = entity.span
            assert 0 <= s < e <= T, self
        for relation in self.relations:
            s, e = relation.head
            assert 0 <= s < e <= T, self
            s, e = relation.tail
            assert 0 <= s < e <= T, self
            for qualifier in relation.qualifiers:
                s, e = qualifier.span
                assert 0 <= s < e <= T, self
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relations:
            assert relation.head in self.entities_by_span, self
            assert relation.tail in self.entities_by_span, self
        return self


__all__ = [
    "HyperREDEntity",
    "HyperREDQualifier",
    "HyperREDRelation",
    "HyperREDUnit",
]

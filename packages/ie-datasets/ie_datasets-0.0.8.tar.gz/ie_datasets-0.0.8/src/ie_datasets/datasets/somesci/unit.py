from functools import cached_property
from typing import Mapping, Sequence

from pybrat.parser import Entity, Example, Relation
from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel
from ie_datasets.util.iter import only


class SoMeSciEntity(ImmutableModel):
    id: str
    mention: str
    entity_type: str
    start: int
    end: int

    @model_validator(mode="after")
    def validate_start_end(self):
        assert 0 <= self.start < self.end
        return self

    @staticmethod
    def from_brat(entity: Entity) -> "SoMeSciEntity":
        assert entity.id is not None
        span = only(entity.spans)
        assert len(entity.references) == 0
        return SoMeSciEntity(
            id=entity.id,
            mention=entity.mention,
            entity_type=entity.type,
            start=span.start,
            end=span.end,
        )


class SoMeSciRelation(ImmutableModel):
    id: str
    argument_1_id: str
    argument_2_id: str
    relation_type: str

    @staticmethod
    def from_brat(relation: Relation) -> "SoMeSciRelation":
        assert relation.id is not None
        assert relation.arg1.id is not None
        assert relation.arg2.id is not None
        return SoMeSciRelation(
            id=relation.id,
            argument_1_id=relation.arg1.id,
            argument_2_id=relation.arg2.id,
            relation_type=relation.type,
        )


class SoMeSciUnit(ImmutableModel):
    id: str
    text: str
    entities: Sequence[SoMeSciEntity]
    relations: Sequence[SoMeSciRelation]

    @staticmethod
    def from_brat(example: Example) -> "SoMeSciUnit":
        assert example.id is not None
        assert isinstance(example.text, str)
        assert len(example.events) == 0
        return SoMeSciUnit(
            id=example.id,
            text=example.text,
            entities=[SoMeSciEntity.from_brat(e) for e in example.entities],
            relations=[SoMeSciRelation.from_brat(r) for r in example.relations],
        )

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_entities(self) -> int:
        return len(self.entities)

    @property
    def num_relations(self) -> int:
        return len(self.relations)

    @cached_property
    def entities_by_id(self) -> Mapping[str, SoMeSciEntity]:
        entities_by_id = {entity.id: entity for entity in self.entities}
        assert len(entities_by_id) == self.num_entities
        return entities_by_id

    @cached_property
    def relations_by_id(self) -> Mapping[str, SoMeSciRelation]:
        relations_by_id = {relation.id: relation for relation in self.relations}
        assert len(relations_by_id) == self.num_relations
        return relations_by_id

    @model_validator(mode="after")
    def sort_sequences(self):
        with self._unfreeze():
            self.entities = sorted(self.entities, key=lambda e: e.id)
            self.relations = sorted(self.relations, key=lambda r: r.id)
        return self

    @model_validator(mode="after")
    def validate_entities(self):
        for e in self.entities:
            assert e.end <= self.num_chars
            assert self.text[e.start:e.end] == e.mention
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for r in self.relations:
            assert r.argument_1_id in self.entities_by_id
            assert r.argument_2_id in self.entities_by_id
        return self


__all__ = [
    "SoMeSciEntity",
    "SoMeSciRelation",
    "SoMeSciUnit",
]

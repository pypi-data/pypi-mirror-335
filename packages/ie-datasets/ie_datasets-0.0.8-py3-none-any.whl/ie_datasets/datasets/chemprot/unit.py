from enum import StrEnum
from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class ChemProtEntityTypeName(StrEnum):
    CHEMICAL = "CHEMICAL"
    GENE_N = "GENE-N"
    GENE_Y = "GENE-Y"


class ChemProtRelationTypeName(StrEnum):
    CPR_0 = "CPR:0"
    CPR_1 = "CPR:1"
    CPR_2 = "CPR:2"
    CPR_3 = "CPR:3"
    CPR_4 = "CPR:4"
    CPR_5 = "CPR:5"
    CPR_6 = "CPR:6"
    CPR_7 = "CPR:7"
    CPR_8 = "CPR:8"
    CPR_9 = "CPR:9"
    CPR_10 = "CPR:10"


class ChemProtEntityMention(ImmutableModel):
    id: str
    entity_type: ChemProtEntityTypeName
    text: str
    start: int
    end: int


class ChemProtRelation(ImmutableModel):
    relation_type: ChemProtRelationTypeName
    argument_1: str
    argument_2: str


class ChemProtUnit(ImmutableModel):
    pmid: int
    text: str
    entities: Sequence[ChemProtEntityMention]
    relations: Sequence[ChemProtRelation]

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_entity_mentions(self) -> int:
        return len(self.entities)

    @property
    def num_relations(self) -> int:
        return len(self.relations)

    @cached_property
    def entities_by_id(self) -> Mapping[str, ChemProtEntityMention]:
        entities_by_id = {entity.id: entity for entity in self.entities}
        assert len(entities_by_id) == self.num_entity_mentions
        return entities_by_id

    @model_validator(mode="after")
    def validate_entities(self):
        for entity in self.entities:
            assert self.text[entity.start:entity.end] == entity.text
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relations:
            assert relation.argument_1 in self.entities_by_id
            assert relation.argument_2 in self.entities_by_id
        return self


__all__ = [
    "ChemProtEntityMention",
    "ChemProtEntityTypeName",
    "ChemProtRelation",
    "ChemProtRelationTypeName",
    "ChemProtUnit",
]

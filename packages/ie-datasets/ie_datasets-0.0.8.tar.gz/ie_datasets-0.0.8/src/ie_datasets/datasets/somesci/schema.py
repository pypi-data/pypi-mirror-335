from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.datasets.somesci.unit import SoMeSciUnit
from ie_datasets.util.interfaces import ImmutableModel


class SoMeSciEntityType(ImmutableModel):
    name: str


class SoMeSciRelationType(ImmutableModel):
    name: str
    argument_1_types: Sequence[str]
    argument_2_types: Sequence[str]

    @model_validator(mode="after")
    def sort_types(self):
        with self._unfreeze():
            self.argument_1_types = sorted(set(self.argument_1_types))
            self.argument_2_types = sorted(set(self.argument_2_types))
        return self


class SoMeSciSchema(ImmutableModel):
    entity_types: Sequence[SoMeSciEntityType]
    relation_types: Sequence[SoMeSciRelationType]

    @cached_property
    def entity_types_by_name(self) -> Mapping[str, SoMeSciEntityType]:
        entity_types_by_name = {
            entity_type.name: entity_type
            for entity_type in self.entity_types
        }
        assert len(entity_types_by_name) == len(self.entity_types)
        return entity_types_by_name

    @cached_property
    def relation_types_by_name(self) -> Mapping[str, SoMeSciRelationType]:
        relation_types_by_name = {
            relation_type.name: relation_type
            for relation_type in self.relation_types
        }
        assert len(relation_types_by_name) == len(self.relation_types)
        return relation_types_by_name

    @model_validator(mode="after")
    def sort_types(self):
        with self._unfreeze():
            self.entity_types = sorted(self.entity_types, key=lambda x: x.name)
            self.relation_types = sorted(self.relation_types, key=lambda x: x.name)
        return self

    @model_validator(mode="after")
    def validate_relation_types(self):
        for relation_type in self.relation_types:
            for type_name in relation_type.argument_1_types:
                assert type_name in self.entity_types_by_name, type_name
            for type_name in relation_type.argument_2_types:
                assert type_name in self.entity_types_by_name, type_name
        return self

    def validate_unit(self, unit: SoMeSciUnit):
        for entity in unit.entities:
            assert entity.entity_type in self.entity_types_by_name
        for relation in unit.relations:
            assert relation.relation_type in self.relation_types_by_name


__all__ = [
    "SoMeSciEntityType",
    "SoMeSciRelationType",
    "SoMeSciSchema",
]

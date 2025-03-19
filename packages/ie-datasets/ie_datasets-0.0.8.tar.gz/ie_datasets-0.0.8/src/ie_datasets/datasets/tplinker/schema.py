from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.datasets.tplinker.unit import TPLinkerUnit
from ie_datasets.util.interfaces import ImmutableModel


class TPLinkerRelationType(ImmutableModel):
    id: int
    name: str


class TPLinkerSchema(ImmutableModel):
    relation_types: Sequence[TPLinkerRelationType]

    @property
    def num_relation_types(self) -> int:
        return len(self.relation_types)

    @cached_property
    def relation_types_by_id(self) -> Mapping[int, TPLinkerRelationType]:
        relation_types_by_id = {
            relation_type.id: relation_type
            for relation_type in self.relation_types
        }
        assert len(relation_types_by_id) == len(self.relation_types)
        return relation_types_by_id

    @cached_property
    def relation_types_by_name(self) -> Mapping[str, TPLinkerRelationType]:
        relation_types_by_name = {
            relation_type.name: relation_type
            for relation_type in self.relation_types
        }
        assert len(relation_types_by_name) == len(self.relation_types)
        return relation_types_by_name

    @model_validator(mode="after")
    def sort_sequences(self):
        with self._unfreeze():
            self.relation_types = sorted(
                self.relation_types,
                key=(lambda relation_type: relation_type.id),
            )
        return self

    def validate_unit(self, unit: TPLinkerUnit):
        for relation in unit.relation_list:
            assert relation.predicate in self.relation_types_by_name

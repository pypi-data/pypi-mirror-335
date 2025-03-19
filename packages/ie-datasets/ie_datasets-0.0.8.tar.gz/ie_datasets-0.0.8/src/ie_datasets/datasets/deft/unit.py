from enum import StrEnum
from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class DEFTEntityType(StrEnum):
    TERM = "Term"
    ALIAS_TERM = "Alias-Term"
    ORDERED_TERM = "Ordered-Term"
    REFERENTIAL_TERM = "Referential-Term"
    DEFINITION = "Definition"
    SECONDARY_DEFINITION = "Secondary-Definition"
    ORDERED_DEFINITION = "Ordered-Definition"
    REFERENTIAL_DEFINITION = "Referential-Definition"
    QUALIFIER = "Qualifier"
    DEFINITION_FRAGMENT = "Definition-frag"


class DEFTRelationType(StrEnum):
    DIRECT_DEFINES = "Direct-Defines"
    INDIRECT_DEFINES = "Indirect-Defines"
    REFERS_TO = "Refers-To"
    ALSO_KNOWN_AS = "AKA"
    SUPPLEMENTS = "Supplements"
    FRAGMENT = "fragment"


class DEFTEntity(ImmutableModel):
    id: str
    entity_type: DEFTEntityType
    text: str
    start_char: int
    end_char: int


class DEFTRelation(ImmutableModel):
    root_id: str
    child_id: str
    relation_type: DEFTRelationType


class DEFTUnit(ImmutableModel):
    source: str
    id: int
    text: str
    entities: Sequence[DEFTEntity]
    relations: Sequence[DEFTRelation]

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
    def entities_by_id(self) -> Mapping[str, DEFTEntity]:
        entities_by_id = {entity.id: entity for entity in self.entities}
        assert len(entities_by_id) == len(self.entities), self
        return entities_by_id

    @model_validator(mode="after")
    def sort_and_deduplicate_sequences(self):
        with self._unfreeze():
            self.entities = sorted(
                set(self.entities),
                key=lambda e: e.id,
            )
            self.relations = sorted(
                set(self.relations),
                key=(lambda r: (r.root_id, r.child_id)),
            )
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relations:
            assert relation.root_id in self.entities_by_id, self
            assert relation.child_id in self.entities_by_id, self
        return self

    @model_validator(mode="after")
    def validate_spans(self):
        for entity in self.entities:
            s = entity.start_char
            e = entity.end_char
            assert 0 <= s < e <= len(self.text)
            assert self.text[s:e] == entity.text
        return self


__all__ = [
    "DEFTEntity",
    "DEFTEntityType",
    "DEFTRelation",
    "DEFTRelationType",
    "DEFTUnit",
]

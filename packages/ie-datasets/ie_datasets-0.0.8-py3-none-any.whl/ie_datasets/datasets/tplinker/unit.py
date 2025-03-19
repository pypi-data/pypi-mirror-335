from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class TPLinkerEntity(ImmutableModel):
    text: str
    char_span: tuple[int, int]


class TPLinkerRelation(ImmutableModel):
    subject: str
    object: str
    subj_char_span: tuple[int, int]
    obj_char_span: tuple[int, int]
    predicate: str


class TPLinkerUnit(ImmutableModel):
    id: str
    text: str
    entity_list: Sequence[TPLinkerEntity]
    relation_list: Sequence[TPLinkerRelation]

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_entities(self) -> int:
        return len(self.entity_list)

    @property
    def num_relations(self) -> int:
        return len(self.relation_list)

    @cached_property
    def entities_by_char_span(self) -> Mapping[tuple[int, int], TPLinkerEntity]:
        entities_by_char_span = {
            entity.char_span: entity
            for entity in self.entity_list
        }
        # this is not true until after the deduplication validator below
        assert len(entities_by_char_span) == self.num_entities
        return entities_by_char_span

    @model_validator(mode="after")
    def sort_deduplicate_sequences(self):
        with self._unfreeze():
            entities_by_char_span = {
                entity.char_span: entity
                for entity in self.entity_list
            }
            self.entity_list = sorted(
                entities_by_char_span.values(),
                key=(lambda entity: entity.char_span),
            )
            self.relation_list = sorted(
                self.relation_list,
                key=(lambda relation: (relation.subj_char_span, relation.obj_char_span)),
            )
        return self

    @model_validator(mode="after")
    def validate_spans(self):
        for entity in self.entity_list:
            s, e = entity.char_span
            assert 0 <= s < e <= self.num_chars
            assert entity.text == self.text[s:e]
        for relation in self.relation_list:
            s, e = relation.subj_char_span
            assert 0 <= s < e <= self.num_chars
            assert relation.subject == self.text[s:e]
            s, e = relation.obj_char_span
            assert 0 <= s < e <= self.num_chars
            assert relation.object == self.text[s:e]
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relation_list:
            assert relation.subj_char_span in self.entities_by_char_span
            assert relation.obj_char_span in self.entities_by_char_span
        return self


__all__ = [
    "TPLinkerEntity",
    "TPLinkerRelation",
    "TPLinkerUnit",
]

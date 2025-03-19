from enum import StrEnum
from functools import cached_property
from typing import Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class CrossREEntityTypeName(StrEnum):
    ACADEMIC_JOURNAL = "academicjournal"
    ALBUM = "album"
    ALGORITHM = "algorithm"
    ASTRONOMICAL_OBJECT = "astronomicalobject"
    AWARD = "award"
    BAND = "band"
    BOOK = "book"
    CHEMICAL_COMPOUND = "chemicalcompound"
    CHEMICAL_ELEMENT = "chemicalelement"
    CONFERENCE = "conference"
    COUNTRY = "country"
    DISCIPLINE = "discipline"
    ELECTION = "election"
    ENZYME = "enzyme"
    EVENT = "event"
    FIELD = "field"
    LITERARY_GENRE = "literarygenre"
    LOCATION = "location"
    MAGAZINE = "magazine"
    METRIC = "metrics"
    MISCELLANEOUS = "misc"
    MUSICAL_ARTIST = "musicalartist"
    MUSICAL_INSTRUMENT = "musicalinstrument"
    MUSIC_GENRE = "musicgenre"
    ORGANISATION = "organisation"
    PERSON = "person"
    POEM = "poem"
    POLITICAL_PARTY = "politicalparty"
    POLITICIAN = "politician"
    PRODUCT = "product"
    PROGRAMMING_LANGUAGE = "programlang"
    PROTEIN = "protein"
    RESEARCHER = "researcher"
    SCIENTIST = "scientist"
    SONG = "song"
    TASK = "task"
    THEORY = "theory"
    UNIVERSITY = "university"
    WRITER = "writer"

class CrossRERelationTypeName(StrEnum):
    ARTIFACT = "artifact"
    CAUSE_EFFECT = "cause-effect"
    COMPARE = "compare"
    GENERAL_AFFILIATION = "general-affiliation"
    NAMED = "named"
    OPPOSITE = "opposite"
    ORIGIN = "origin"
    PART_OF = "part-of"
    PHYSICAL = "physical"
    RELATED_TO = "related-to"
    ROLE = "role"
    SOCIAL = "social"
    TEMPORAL = "temporal"
    TOPIC = "topic"
    TYPE_OF = "type-of"
    USAGE = "usage"
    WIN_DEFEAT = "win-defeat"


class CrossREEntity(ImmutableModel):
    start: int
    end: int
    entity_type: CrossREEntityTypeName


class CrossRERelation(ImmutableModel):
    head_start: int
    head_end: int
    tail_start: int
    tail_end: int
    relation_type: CrossRERelationTypeName
    explanation: str
    uncertain: bool
    syntax_ambiguity: bool


class CrossREUnit(ImmutableModel):
    doc_key: str
    sentence: Sequence[str]
    ner: Sequence[tuple[int, int, CrossREEntityTypeName]]
    relations: Sequence[tuple[int, int, int, int, CrossRERelationTypeName, str, bool, bool]]

    @cached_property
    def text(self) -> str:
        return " ".join(self.sentence)

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_tokens(self) -> int:
        return len(self.sentence)

    @property
    def num_entities(self) -> int:
        return len(self.entity_objects)

    @property
    def num_relations(self) -> int:
        return len(self.relation_objects)

    @model_validator(mode="after")
    def sort_sequences(self):
        with self._unfreeze():
            self.ner = sorted(self.ner)
            self.relations = sorted(self.relations)
        return self

    @cached_property
    def _token_spans(self) -> Sequence[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        offset = 0
        for token in self.sentence:
            start = offset
            end = start + len(token)
            spans.append((start, end))
            offset = end + 1
        return spans

    def token_span_to_char_span(self, start: int, end: int) -> tuple[int, int]:
        assert 0 <= start <= end < self.num_tokens
        return self._token_spans[start][0], self._token_spans[end][1]

    @cached_property
    def entity_objects(self) -> Sequence[CrossREEntity]:
        entities: list[CrossREEntity] = []
        for start, end, entity_type in self.ner:
            start, end = self.token_span_to_char_span(start, end)
            entity = CrossREEntity(
                start=start,
                end=end,
                entity_type=entity_type,
            )
            entities.append(entity)
        return entities

    @cached_property
    def entities_by_span(self) -> dict[tuple[int, int], CrossREEntity]:
        entities_by_span = {
            (entity.start, entity.end): entity
            for entity in self.entity_objects
        }
        assert len(entities_by_span) == self.num_entities
        return entities_by_span

    @cached_property
    def relation_objects(self) -> Sequence[CrossRERelation]:
        relations: list[CrossRERelation] = []
        for (
            head_start,
            head_end,
            tail_start,
            tail_end,
            relation_type,
            explanation,
            uncertain,
            syntax_ambiguity,
        ) in self.relations:
            head_start, head_end = self.token_span_to_char_span(head_start, head_end)
            tail_start, tail_end = self.token_span_to_char_span(tail_start, tail_end)
            relation = CrossRERelation(
                head_start=head_start,
                head_end=head_end,
                tail_start=tail_start,
                tail_end=tail_end,
                relation_type=relation_type,
                explanation=explanation,
                uncertain=uncertain,
                syntax_ambiguity=syntax_ambiguity,
            )
            relations.append(relation)
        return relations

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relation_objects:
            assert (relation.head_start, relation.head_end) in self.entities_by_span
            assert (relation.tail_start, relation.tail_end) in self.entities_by_span
        return self

    @property
    def has_uncertain_relation(self) -> bool:
        return any(relation.uncertain for relation in self.relation_objects)


__all__ = [
    "CrossREEntity",
    "CrossREEntityTypeName",
    "CrossRERelation",
    "CrossRERelationTypeName",
    "CrossREUnit",
]

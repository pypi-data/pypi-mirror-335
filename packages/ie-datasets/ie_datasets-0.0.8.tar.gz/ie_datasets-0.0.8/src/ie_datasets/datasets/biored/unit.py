from collections import defaultdict
from functools import cached_property
from typing import Literal, Mapping, Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class BioREDSpan(ImmutableModel):
    offset: int
    length: int

    @property
    def end(self) -> int:
        return self.offset + self.length


class BioREDEntityMentionInfons(ImmutableModel):
    identifier: str
    type: str


class BioREDEntityMention(ImmutableModel):
    id: int
    infons: BioREDEntityMentionInfons
    text: str
    locations: Sequence[BioREDSpan]

    @property
    def identifiers(self) -> Sequence[str]:
        return self.infons.identifier.split(",")

    @property
    def entity_type(self) -> str:
        return self.infons.type


class BioREDPassage(ImmutableModel):
    offset: int
    text: str
    annotations: Sequence[BioREDEntityMention]

    @property
    def end(self) -> int:
        return self.offset + len(self.text)

    @model_validator(mode="after")
    def validate_spans(self):
        for entity in self.annotations:
            for span in entity.locations:
                assert self.offset <= span.offset < span.end <= self.end
                assert self.text[span.offset-self.offset:span.end-self.offset] == entity.text
        return self


class BioREDRelationInfons(ImmutableModel):
    entity1: str
    entity2: str
    type: str
    novel: Literal["Novel", "No"]


class BioREDRelation(ImmutableModel):
    id: str
    infons: BioREDRelationInfons

    @property
    def entity_1_identifier(self) -> str:
        return self.infons.entity1

    @property
    def entity_2_identifier(self) -> str:
        return self.infons.entity2

    @property
    def relation_type(self) -> str:
        return self.infons.type

    @property
    def is_novel(self) -> bool:
        return self.infons.novel == "Novel"


class BioREDUnit(ImmutableModel):
    id: str
    passages: tuple[BioREDPassage, BioREDPassage]
    relations: Sequence[BioREDRelation]

    @property
    def title_passage(self) -> BioREDPassage:
        return self.passages[0]

    @property
    def title(self) -> str:
        return self.title_passage.text

    @property
    def abstract_passage(self) -> BioREDPassage:
        return self.passages[1]

    @property
    def abstract(self) -> str:
        return self.abstract_passage.text

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.abstract}"

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_passages(self) -> int:
        return len(self.passages)

    @property
    def num_entity_mentions(self) -> int:
        return len(self.entity_mentions_by_id)

    @property
    def num_entities(self) -> int:
        return len(self.entity_mentions_by_identifier)

    @property
    def num_relations(self) -> int:
        return len(self.relations)

    @cached_property
    def entity_mentions_by_id(self) -> Mapping[int, BioREDEntityMention]:
        entity_mentions_by_id = {
            entity.id: entity
            for passage in self.passages
            for entity in passage.annotations
        }
        assert len(entity_mentions_by_id) == sum(
            len(passage.annotations) for passage in self.passages
        )
        return entity_mentions_by_id

    @cached_property
    def entity_mentions_by_identifier(self) -> Mapping[str, Sequence[BioREDEntityMention]]:
        entity_mentions_by_identifier: dict[str, list[BioREDEntityMention]] = defaultdict(list)
        for passage in self.passages:
            for entity in passage.annotations:
                for identifier in entity.identifiers:
                    entity_mentions_by_identifier[identifier].append(entity)
        return {
            identifier: tuple(entities)
            for identifier, entities in entity_mentions_by_identifier.items()
        }

    @model_validator(mode="after")
    def validate_text(self):
        assert self.abstract_passage.offset == len(self.title) + 1
        return self

    @model_validator(mode="after")
    def validate_relations(self):
        for relation in self.relations:
            assert relation.entity_1_identifier in self.entity_mentions_by_identifier
            assert relation.entity_2_identifier in self.entity_mentions_by_identifier
        return self


__all__ = [
    "BioREDEntityMentionInfons",
    "BioREDEntityMention",
    "BioREDPassage",
    "BioREDRelationInfons",
    "BioREDRelation",
    "BioREDSpan",
    "BioREDUnit",
]

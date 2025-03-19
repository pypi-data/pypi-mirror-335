from functools import cached_property
from typing import Mapping, Sequence

from pydantic import model_validator

from ie_datasets.datasets.wikievents.unit import WikiEventsUnit
from ie_datasets.util.interfaces import ImmutableModel


class WikiEventsEntityType(ImmutableModel):
    name: str
    definition: str


class WikiEventsEventType(ImmutableModel):
    name: str
    event_id: str
    template: str
    keywords: Sequence[str]
    roles: Sequence[str] # may contain duplicates
    role_types: Sequence[Sequence[str]]

    @cached_property
    def role_types_by_role(self) -> Mapping[str, frozenset[str]]:
        role_types: dict[str, frozenset[str]] = {}
        for role, types in zip(self.roles, self.role_types):
            types_set = frozenset(types)
            assert len(types_set) == len(types)
            if role in role_types:
                assert types_set == role_types[role], types_set
            else:
                role_types[role] = types_set
        return role_types

    @model_validator(mode="after")
    def check_roles(self):
        assert (
            len(self.roles)
            == len(self.role_types)
            >= len(self.role_types_by_role)
        )
        return self

    @model_validator(mode="after")
    def check_template(self):
        for i in range(1, 1+len(self.roles)):
            arg_str = f"<arg{i}>"
            assert arg_str in self.template
        return self


class WikiEventsOntology(ImmutableModel):
    entity_types: Sequence[WikiEventsEntityType]
    event_types: Sequence[WikiEventsEventType]

    @cached_property
    def entity_types_by_name(self) -> Mapping[str, WikiEventsEntityType]:
        types: dict[str, WikiEventsEntityType] = {}
        for entity_type in self.entity_types:
            assert entity_type.name not in types
            types[entity_type.name] = entity_type
        return types

    @cached_property
    def event_types_by_name(self) -> Mapping[str, WikiEventsEventType]:
        types: dict[str, WikiEventsEventType] = {}
        for event_type in self.event_types:
            assert event_type.name not in types
            types[event_type.name] = event_type
        return types

    @model_validator(mode="after")
    def check_entity_types(self):
        assert len(self.entity_types_by_name) == len(self.entity_types)
        return self

    @model_validator(mode="after")
    def check_event_types(self):
        assert len(self.event_types_by_name) == len(self.event_types)
        for event_type in self.event_types:
            for types in event_type.role_types:
                for t in types:
                    assert t in self.entity_types_by_name
        return self

    def validate_unit(self, unit: WikiEventsUnit):
        for mention in unit.entity_mentions:
            assert mention.entity_type in self.entity_types_by_name

        for mention in unit.event_mentions:
            event_type = self.event_types_by_name[mention.event_type]
            for argument in mention.arguments:
                entity = unit.entity_mentions_by_id[argument.entity_id]
                role_types = event_type.role_types_by_role[argument.role]
                assert entity.entity_type in role_types


__all__ = [
    "WikiEventsEntityType",
    "WikiEventsEventType",
    "WikiEventsOntology",
]

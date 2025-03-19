from functools import cached_property
from typing import Annotated, Mapping, Sequence

from annotated_types import Ge
from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel


class WikiEventsWordSpan(ImmutableModel):
    start: Annotated[int, Ge(0)]
    end: Annotated[int, Ge(0)]
    text: str
    sent_idx: Annotated[int, Ge(0)]

    @model_validator(mode="after")
    def check_indices_correct(self):
        assert 0 <= self.start < self.end
        return self


class WikiEventsEntityMention(WikiEventsWordSpan):
    id: str
    entity_type: str
    mention_type: str


class WikiEventsEventTrigger(WikiEventsWordSpan):
    pass


class WikiEventsEventArgument(ImmutableModel):
    entity_id: str
    role: str
    text: str


class WikiEventsEventMention(ImmutableModel):
    id: str
    event_type: str
    trigger: WikiEventsEventTrigger
    arguments: Sequence[WikiEventsEventArgument]


class WikiEventsCoreferences(ImmutableModel):
    doc_key: str
    clusters: Sequence[Sequence[str]]
    informative_mentions: Sequence[str]

    @model_validator(mode="after")
    def check_paired(self):
        assert len(self.clusters) == len(self.informative_mentions)
        return self


class WikiEventsUnit(ImmutableModel):
    doc_id: str
    tokens: Sequence[str]
    text: str
    sentences: Sequence[tuple[Sequence[tuple[str, int, int]], str]]
    entity_mentions: Sequence[WikiEventsEntityMention]
    event_mentions: Sequence[WikiEventsEventMention]
    coreferences: WikiEventsCoreferences

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_tokens(self) -> int:
        return len(self.tokens)

    @property
    def num_sentences(self) -> int:
        return len(self.sentences)

    @property
    def num_entity_mentions(self) -> int:
        return len(self.entity_mentions)

    @property
    def num_event_mentions(self) -> int:
        return len(self.event_mentions)

    @cached_property
    def token_spans(self) -> Sequence[tuple[int, int]]:
        return [
            (start, end)
            for sentence, _ in self.sentences
            for _, start, end in sentence
        ]

    @cached_property
    def entity_mentions_by_id(self) -> Mapping[str, WikiEventsEntityMention]:
        return {
            e.id: e
            for e in self.entity_mentions
        }

    @cached_property
    def event_mentions_by_id(self) -> Mapping[str, WikiEventsEventMention]:
        return {
            e.id: e
            for e in self.event_mentions
        }

    @cached_property
    def entity_names_by_entity_mention(self) -> Mapping[str, str]:
        assert self.coreferences.doc_key == self.doc_id
        names: dict[str, str] = {}
        for cluster, name in zip(
            self.coreferences.clusters,
            self.coreferences.informative_mentions,
            strict=True,
        ):
            for mention_id in cluster:
                assert mention_id not in names
                names[mention_id] = name
        return names

    @cached_property
    def entity_mentions_by_entity_name(self) -> Mapping[str, frozenset[str]]:
        assert self.coreferences.doc_key == self.doc_id
        mentions: dict[str, frozenset[str]] = {}
        for name, cluster in zip(
            self.coreferences.informative_mentions,
            self.coreferences.clusters,
            strict=True,
        ):
            cluster_set = frozenset(cluster)
            assert len(cluster_set) == len(cluster)
            mentions[name] = cluster_set
        return mentions

    @model_validator(mode="after")
    def fix_text_whitespace(self):
        """
        The start and end bounds of each token cannot be used on self.text.
        The offsets account for whitespace between sentences, which is deleted
        in self.text.
        Instead, the original text should be reconstructed by concatenating the
        sentences, with faithful amounts of whitespace inserted between them.
        """
        text = ""
        for tokens, sentence in self.sentences:
            _, start, _ = tokens[0]
            assert len(text) <= start
            text = text.ljust(start) + sentence.strip()

            for token, start, end in tokens:
                assert text[start:end] == token

        with self._unfreeze():
            self.text = text
        return self

    @model_validator(mode="after")
    def check_entities(self):
        entity_ids = set(e.id for e in self.entity_mentions)
        assert len(entity_ids) == len(self.entity_mentions)

        for em in self.event_mentions:
            for a in em.arguments:
                assert a.entity_id in entity_ids

        return self

    @model_validator(mode="after")
    def check_spans(self):
        """
        Must run after self.fix_text_whitespace.
        """
        for e in self.entity_mentions:
            start, end = self.get_char_span(e.start, e.end)
            assert self.text[start:end] == e.text

        for e in self.event_mentions:
            start, end = self.get_char_span(e.trigger.start, e.trigger.end)
            assert self.text[start:end] == e.trigger.text
            for a in e.arguments:
                assert a.text == self.entity_mentions_by_id[a.entity_id].text

        return self

    def get_char_span(
            self,
            start_token: int,
            end_token: int,
    ) -> tuple[int, int]:
        assert start_token < end_token
        start_char, _ = self.token_spans[start_token]
        _, end_char = self.token_spans[end_token - 1]
        return start_char, end_char


__all__ = [
    "WikiEventsCoreferences",
    "WikiEventsEntityMention",
    "WikiEventsEventArgument",
    "WikiEventsEventMention",
    "WikiEventsEventTrigger",
    "WikiEventsUnit",
]

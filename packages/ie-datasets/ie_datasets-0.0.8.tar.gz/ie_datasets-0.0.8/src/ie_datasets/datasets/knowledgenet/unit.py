from typing import Literal, Sequence, TypeAlias
from ie_datasets.util.interfaces import ImmutableModel


KnowledgeNetFold: TypeAlias = Literal[1, 2, 3, 4, 5]


class KnowledgeNetProperty(ImmutableModel):
    propertyId: str
    propertyName: str
    propertyDescription: str


class KnowledgeNetFact(ImmutableModel):
    factId: str
    propertyId: str
    humanReadable: str
    annotatedPassage: str
    subjectStart: int
    subjectEnd: int
    subjectText: str
    subjectUri: str
    objectStart: int
    objectEnd: int
    objectText: str
    objectUri: str


class KnowledgeNetPassage(ImmutableModel):
    passageId: str
    passageStart: int
    passageEnd: int
    passageText: str
    exhaustivelyAnnotatedProperties: Sequence[KnowledgeNetProperty]
    facts: Sequence[KnowledgeNetFact]

    @property
    def num_chars(self) -> int:
        return len(self.passageText)

    @property
    def num_facts(self) -> int:
        return len(self.facts)


class KnowledgeNetUnit(ImmutableModel):
    fold: KnowledgeNetFold
    documentId: str
    source: str
    documentText: str
    passages: Sequence[KnowledgeNetPassage]

    @property
    def num_chars(self) -> int:
        return len(self.documentText)

    @property
    def num_passages(self) -> int:
        return len(self.passages)

    @property
    def num_facts(self) -> int:
        return sum(p.num_facts for p in self.passages)


__all__ = [
    "KnowledgeNetFact",
    "KnowledgeNetFold",
    "KnowledgeNetPassage",
    "KnowledgeNetProperty",
    "KnowledgeNetUnit",
]

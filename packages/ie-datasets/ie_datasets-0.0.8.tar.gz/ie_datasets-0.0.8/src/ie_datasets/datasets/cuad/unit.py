from typing import Sequence

from pydantic import model_validator

from ie_datasets.util.interfaces import ImmutableModel
from ie_datasets.util.iter import only


class CUADAnswer(ImmutableModel):
    text: str
    answer_start: int


class CUADQuestionAnswer(ImmutableModel):
    id: str
    answers: Sequence[CUADAnswer]
    question: str
    is_impossible: bool

    @property
    def num_answers(self) -> int:
        return len(self.answers)

    @model_validator(mode="after")
    def sort_answers(self):
        with self._unfreeze():
            self.answers = sorted(self.answers, key=lambda answer: answer.answer_start)
        return self


class CUADParagraph(ImmutableModel):
    context: str
    qas: Sequence[CUADQuestionAnswer]

    @model_validator(mode="after")
    def sort_qas(self):
        with self._unfreeze():
            self.qas = sorted(self.qas, key=lambda qa: qa.id)
        return self


class CUADUnit(ImmutableModel):
    title: str
    paragraphs: tuple[CUADParagraph] # it's always just 1

    @property
    def paragraph(self) -> CUADParagraph:
        return only(self.paragraphs)

    @property
    def text(self) -> str:
        return self.paragraph.context

    @property
    def num_chars(self) -> int:
        return len(self.text)

    @property
    def num_questions(self) -> int:
        return len(self.paragraph.qas)

    @property
    def num_answers(self) -> int:
        return sum(qa.num_answers for qa in self.paragraph.qas)

    @model_validator(mode="after")
    def validate_answers(self):
        for qa in self.paragraph.qas:
            for answer in qa.answers:
                start = answer.answer_start
                end = start + len(answer.text)
                assert 0 <= start < end <= self.num_chars
                assert self.text[start:end] == answer.text
        return self


__all__ = [
    "CUADAnswer",
    "CUADParagraph",
    "CUADQuestionAnswer",
    "CUADUnit",
]

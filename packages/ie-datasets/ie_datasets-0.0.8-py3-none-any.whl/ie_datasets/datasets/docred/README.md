# DocRED

**ACL 2019**: [DocRED: A Large-Scale Document-Level Relation Extraction Dataset](https://aclanthology.org/P19-1074/)

**GitHub**: [`thunlp/DocRED`](https://github.com/thunlp/DocRED)

[**Google Drive**](https://drive.google.com/drive/folders/1c5-0YwnoJx8NS6CV2f-NoTHR__BdkNqw?usp=drive_link)


## Splits

DocRED has both a human-annotated train split and an extremely large distantly-labelled train split.
However, the test set of DocRED lacks labels.


## Schema

Tables 9 and 10 in the appendix of the ACL 2019 paper contain extensive definitions for every entity and relation type.


## Quirks

- We convert all field names to standard Python snake case.
- A small number of entities have multiple entity types among their mentions.
  This is usually a mistake.

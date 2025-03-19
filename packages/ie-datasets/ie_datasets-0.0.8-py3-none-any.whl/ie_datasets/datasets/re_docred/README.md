# Re-DocRED

**EMNLP 2022**: [Revisiting DocRED - Addressing the False Negative Problem in Relation Extraction](https://aclanthology.org/2022.emnlp-main.580/)

**GitHub**: [`tonytan48/Re-DocRED`](https://github.com/tonytan48/Re-DocRED)

Re-DocRED is a re-annotation of the entire [DocRED](../docred/README.md) dataset to fix annotation errors.


## Splits

Unlike DocRED, Re-DocRED lacks a large distantly-labelled split, but its test set includes labels.


## Schema

Re-DocRED uses the exact same schema as DocRED.
Tables 9 and 10 in the appendix of the [DocRED paper](https://aclanthology.org/P19-1074/) contain extensive definitions for every entity and relation type.


## Quirks

- Compared to DocRED data, the data contains an additional `global_pos` and `index` fields which do not provide any useful information that could not be deduced by the rest of the data.
  Thus, we drop these fields such that the data remains completely compatible with DocRED dataset types.
- A small number of entities have multiple entity types among their mentions.
  This is usually a mistake.

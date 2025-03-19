# ChemProt

[**Website**](https://biocreative.bioinformatics.udel.edu/tasks/biocreative-vi/track-5/) (defunct)

**Hugging Face**: [`bigbio/chemprot`](https://huggingface.co/datasets/bigbio/chemprot)

[**Annotation Guidelines**](https://zenodo.org/records/4957138)

## Availability

This dataset is no longer publicly available from the original source.
It is cloned on Hugging Face at `bigbio/chemprot`, but running `datasets.load_dataset("bigbio/chemprot")` will not work since it pulls the data from the same site.
However, Hugging Face has saved [Parquet files](https://huggingface.co/datasets/bigbio/chemprot/tree/refs%2Fconvert%2Fparquet) of the dataset from before the original source went down; these files serve as the only known publicly available backup of the dataset.

## Schema

ChemProt follows a relation type hierarchy, with each "relation type" being a group of relation sub-types, all thoroughly defined in the annotation guidelines.
The original data was annotated at the sub-type level, but standard evaluations on ChemProt use the larger groups.
Each group has been given a name by [BigScience Biomedical Datasets (bigbio)](https://huggingface.co/bigbio), the curators of the Hugging Face clone of the dataset.
However, the sub-type labels are not included in the clone.

| Group    | `bigbio` Name    | Relation Sub-types                                      |
| -------- | ---------------- | ------------------------------------------------------- |
| `CPR:0`  |  `Undefined`     | `UNDEFINED`                                             |
| `CPR:1`  |  `Part_of`       | `PART_OF`                                               |
| `CPR:2`  |  `Regulator`     | `REGULATOR` `DIRECT_REGULATOR` `INDIRECT_REGULATOR`     |
| `CPR:3`  |  `Upregulator`   | `UPREGULATOR` `ACTIVATOR` `INDIRECT_UPREGULATOR`        |
| `CPR:4`  |  `Downregulator` | `DOWNREGULATOR` `INHIBITOR` `INDIRECT_DOWNREGULATOR`    |
| `CPR:5`  |  `Agonist`       | `AGONIST` `AGONIST-­‐ACTIVATOR` `AGONIST-­‐INHIBITOR`     |
| `CPR:6`  |  `Antagonist`    | `ANTAGONIST`                                            |
| `CPR:7`  |  `Modulator`     | `MODULATOR` `MODULATOR-ACTIVATOR` `MODULATOR-INHIBITOR` |
| `CPR:8`  |  `Cofactor`      | `COFACTOR`                                              |
| `CPR:9`  |  `Substrate`     | `SUBSTRATE` `PRODUCT_OF` `SUBSTRATE_PRODUCT_OF`         |
| `CPR:10` |  `Not`           | `NOT`                                                   |

Only groups `CPR:3` through `CPR:6` (inclusive) are used for standard evaluations on ChemProt.

## Quirks

- The `UNDEFINED` relation type is officially part of the original annotations, but it is not mentioned in any of the dataset documentation.
  Across the entire dataset, there are only 3 relations (1 in train, 2 in validation) with this type.

# CrossRE & CrossRE 2.0

**EMNLP 2022**: [CrossRE: A Cross-Domain Dataset for Relation Extraction](https://aclanthology.org/2022.findings-emnlp.263/)

**LREC-COLING 2024**: [How to Encode Domain Information in Relation Classification](https://aclanthology.org/2024.lrec-main.728/)

**GitHub**: [`mainlp/CrossRE`](https://github.com/mainlp/CrossRE)

[**Annotation Guidelines**](https://github.com/mainlp/CrossRE/blob/main/crossre_annotation/CrossRE-annotation-guidelines.pdf)


## Schema

### Entity Types

The `ai`, `literature`, `music`, `politics`, and `science` domains of CrossRE are derived from CrossNER, and inherits the same entity types.
The entity types of CrossRE are defined in the appendix of the paper [CrossNER: Evaluating Cross-Domain Named Entity Recognition](https://arxiv.org/abs/2012.04373).

Meanwhile, the `news` domain of CrossRE is derived from [CoNLL-2003](https://aclanthology.org/W03-0419/), which contains only 3 non-miscellaneous entity types, all of which are self-explanatory:
- `person`
- `organisation`
- `location`

CrossRE 2.0 features more news domain annotations, which we denote `news-2`; it contains the non-miscellaneous entity types
- `country`
- `location`
- `organisation`
- `person`
- `politicalparty`
- `politician`

### Relation Types

The [annotation guidelines](https://github.com/mainlp/CrossRE/blob/main/crossre_annotation/CrossRE-annotation-guidelines.pdf) outline the relation types of CrossRE.
Besides the main relation types which apply across domains, the `explanation` field can include a more specific relation type for the given domain and entity types.

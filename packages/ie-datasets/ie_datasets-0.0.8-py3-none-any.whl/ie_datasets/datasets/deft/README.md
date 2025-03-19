# DEFT

**SIGANN 2019**: [DEFT: A corpus for definition extraction in free- and semi-structured text](https://aclanthology.org/W19-4015/)

**GitHub**: [`adobe-research/deft_corpus`](https://github.com/adobe-research/deft_corpus)

**License**: [CC BY-NC-SA 4.0](https://github.com/adobe-research/deft_corpus?tab=readme-ov-file#licensing-information)

**Google Group**: [DeftEval 2020](https://groups.google.com/g/semeval-2020-task-6-all)


## Errata

The number of samples containing errors is overwhelming.

A running list of errors fixed:

1. Extra line 2308 in `data/deft_files/train/t5_economic_1_202.deft`
2. Extra line 169 in `data/deft_files/dev/t4_psychology_1_0.deft`

The remaining errors are caught by various assertions and dropped:

3. Sample 56 in `t1_biology_0_0.deft` of the training split has erroneously included the heading ("Isotopes") inside the text snippet.
4. Some careless error fixing in the past has resulted in incorrect character spans and tags.
   1. Line 1359 inside sample 74 in `t1_biology_0_0.deft` of the training split.
   2. Line 5125 inside sample 263 in `t1_biology_0_0.deft` of the training split.
   3. Lines 5246 and 5250 inside sample 266 in `t1_biology_0_0.deft` of the training split.
   4. Line 5237 inside sample 269 in `t1_biology_0_0.deft` of the training split.

We will eventually manually fix all the dropped errors ourselves in a fork of `deft_corpus`,

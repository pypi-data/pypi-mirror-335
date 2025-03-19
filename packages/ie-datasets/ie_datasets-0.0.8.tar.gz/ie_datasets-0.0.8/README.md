# Information Extraction Datasets

This package takes care of all of the tedium when loading various information extraction datasets, providing the data in fully validated and typed Pydantic objects.

## Datasets

### [BioRED](./src/ie_datasets/datasets/biored/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import BioRED
  BioRED.load_units(BioRED.Split.TRAIN)
  ```
</details>


### [ChemProt](./src/ie_datasets/datasets/chemprot/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import ChemProt
  ChemProt.load_units(ChemProt.Split.TRAIN)
  ```
</details>


### [CrossRE](./src/ie_datasets/datasets/crossre/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import CrossRE
  CrossRE.load_units(CrossRE.Split.TRAIN, domain=CrossRE.Domain.AI)
  ```
</details>


### [CUAD](./src/ie_datasets/datasets/cuad/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import CUAD
  CUAD.load_units()
  ```
</details>


### [DEFT](./src/ie_datasets/datasets/deft/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import DEFT
  DEFT.load_units(DEFT.Split.TRAIN, category=DEFT.Category.BIOLOGY)
  ```

  > **NOTE**:
  > DEFT's data files contain an overwhelming number of errata.
  > For now, we drop the errors instead of fixing them.
  > This means that we are loading a subset of DEFT, not the full dataset.
</details>


### [DocRED](./src/ie_datasets/datasets/docred/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import DocRED
  DocRED.load_schema()
  DocRED.load_units(DocRED.Split.TRAIN_ANNOTATED)
  ```

  > **NOTE**:
  > DocRED has been superseded by [Re-DocRED](#re-docred)
</details>


### [HyperRED](./src/ie_datasets/datasets/hyperred/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import HyperRED
  HyperRED.load_units(HyperRED.Split.TRAIN)
  ```
</details>


### [KnowledgeNet](./src/ie_datasets/datasets/knowledgenet/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import KnowledgeNet
  KnowledgeNet.load_units(KnowledgeNet.Split.TRAIN)
  ```

  > **NOTE**:
  > The test split of KnowledgeNet is unlabelled.
</details>


### [Re-DocRED](./src/ie_datasets/datasets/re_docred/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import ReDocRED
  ReDocRED.load_schema()
  ReDocRED.load_units(ReDocRED.Split.TRAIN)
  ```
</details>


### [SciERC](./src/ie_datasets/datasets/scierc/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import SciERC
  SciERC.load_units(SciERC.Split.TRAIN)
  ```
</details>


### [SciREX](./src/ie_datasets/datasets/scirex/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import SciREX
  SciREX.load_units(SciREX.Split.TRAIN)
  ```
</details>


### [SoMeSci](./src/ie_datasets/datasets/somesci/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import SoMeSci
  SoMeSci.load_schema()
  SoMeSci.load_units(SoMeSci.Split.TRAIN, group=SoMeSci.Group.CREATION_SENTENCES)
  ```
</details>


### [TPLinker/NYT](./src/ie_datasets/datasets/tplinker/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import TPLinkerNYT
  TPLinkerNYT.load_schema()
  TPLinkerNYT.load_units(TPLinkerNYT.Split.TRAIN)
  ```
</details>


### [TPLinker/WebNLG](./src/ie_datasets/datasets/tplinker/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import TPLinkerWebNLG
  TPLinkerWebNLG.load_schema()
  TPLinkerWebNLG.load_units(TPLinkerWebNLG.Split.TRAIN)
  ```
</details>


### [WikiEvents](./src/ie_datasets/datasets/wikievents/README.md)

<details>
  <summary>Example</summary>

  ```py
  from ie_datasets import WikiEvents
  WikiEvents.load_ontology()
  WikiEvents.load_units(WikiEvents.Split.TRAIN)
  ```
</details>

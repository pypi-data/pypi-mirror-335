from ie_datasets.datasets import (
    biored as BioRED,
    chemprot as ChemProt,
    crossre as CrossRE,
    cuad as CUAD,
    deft as DEFT,
    docred as DocRED,
    hyperred as HyperRED,
    knowledgenet as KnowledgeNet,
    re_docred as ReDocRED,
    scierc as SciERC,
    scirex as SciREX,
    somesci as SoMeSci,
    wikievents as WikiEvents,
)
from ie_datasets.datasets.tplinker import (
    nyt as TPLinkerNYT,
    webnlg as TPLinkerWebNLG,
)


__all__ = [
    "BioRED",
    "ChemProt",
    "CrossRE",
    "CUAD",
    "DEFT",
    "DocRED",
    "HyperRED",
    "KnowledgeNet",
    "ReDocRED",
    "SciERC",
    "SciREX",
    "SoMeSci",
    "TPLinkerNYT",
    "TPLinkerWebNLG",
    "WikiEvents",
]

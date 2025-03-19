from ie_datasets import (
    BioRED,
    ChemProt,
    CrossRE,
    DEFT,
    DocRED,
    HyperRED,
    KnowledgeNet,
    ReDocRED,
    SciERC,
    SciREX,
    SoMeSci,
    TPLinkerNYT,
    TPLinkerWebNLG,
    WikiEvents,
)


def test_biored_summary():
    with open("summaries/BioRED.txt") as f:
        assert f.read().strip("\n") == BioRED.get_summary()


def test_chemprot_summary():
    with open("summaries/ChemProt.txt") as f:
        assert f.read().strip("\n") == ChemProt.get_summary()


def test_crossre_summary():
    with open("summaries/CrossRE.txt") as f:
        assert f.read().strip("\n") == CrossRE.get_summary()


def test_deft_summary():
    with open("summaries/DEFT.txt") as f:
        assert f.read().strip("\n") == DEFT.get_summary()


def test_docred_summary():
    with open("summaries/DocRED.txt") as f:
        assert f.read().strip("\n") == DocRED.get_summary()


def test_hyperred_summary():
    with open("summaries/HyperRED.txt") as f:
        assert f.read().strip("\n") == HyperRED.get_summary()


def test_knowledgenet_summary():
    with open("summaries/KnowledgeNet.txt") as f:
        assert f.read().strip("\n") == KnowledgeNet.get_summary()


def test_re_docred_summary():
    with open("summaries/Re-DocRED.txt") as f:
        assert f.read().strip("\n") == ReDocRED.get_summary()


def test_scierc_summary():
    with open("summaries/SciERC.txt") as f:
        assert f.read().strip("\n") == SciERC.get_summary()


def test_scirex_summary():
    with open("summaries/SciREX.txt") as f:
        assert f.read().strip("\n") == SciREX.get_summary()


def test_somesci_summary():
    with open("summaries/SoMeSci.txt") as f:
        assert f.read().strip("\n") == SoMeSci.get_summary()


def test_tplinker_nyt_summary():
    with open("summaries/TPLinker/NYT.txt") as f:
        assert f.read().strip("\n") == TPLinkerNYT.get_summary()


def test_tplinker_webnlg_summary():
    with open("summaries/TPLinker/WebNLG.txt") as f:
        assert f.read().strip("\n") == TPLinkerWebNLG.get_summary()


def test_wikievents_summary():
    with open("summaries/WikiEvents.txt") as f:
        assert f.read().strip("\n") == WikiEvents.get_summary()


if __name__ == "__main__":
    test_biored_summary()
    test_chemprot_summary()
    test_crossre_summary()
    test_deft_summary()
    test_docred_summary()
    test_hyperred_summary()
    test_knowledgenet_summary()
    test_re_docred_summary()
    test_scierc_summary()
    test_scirex_summary()
    test_somesci_summary()
    test_tplinker_nyt_summary()
    test_tplinker_webnlg_summary()
    test_wikievents_summary()

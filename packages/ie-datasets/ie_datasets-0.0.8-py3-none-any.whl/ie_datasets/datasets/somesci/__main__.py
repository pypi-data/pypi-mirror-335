assert __name__ == "__main__"

from ie_datasets.datasets.somesci.load import (
    load_somesci_schema,
    SoMeSciVersion,
)
from ie_datasets.datasets.somesci.summary import get_somesci_summary

from ie_datasets.util.iter import same


same(load_somesci_schema(v) for v in SoMeSciVersion)
print(get_somesci_summary())

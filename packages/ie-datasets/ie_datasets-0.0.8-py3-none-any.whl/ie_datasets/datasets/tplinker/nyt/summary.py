from ie_datasets.datasets.tplinker.load import TPLinkerSplit
from ie_datasets.datasets.tplinker.nyt.load import (
    load_tplinker_nyt_schema,
    load_tplinker_nyt_units,
)


def get_tplinker_nyt_summary() -> str:
    lines: list[str] = []

    lines.append("=" * 80)
    schema = load_tplinker_nyt_schema()

    lines.append(f"RELATION TYPES: {schema.num_relation_types} types")
    for relation_type in schema.relation_types:
        lines.append(f"  {relation_type.id:2d}: {relation_type.name}")

    for split in TPLinkerSplit:
        lines.append("=" * 80)
        units = list(load_tplinker_nyt_units(split))
        lines.append(f"{split}: {len(units)} units")

    return "\n".join(lines)


__all__ = [
    "get_tplinker_nyt_summary",
]

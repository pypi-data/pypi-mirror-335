from ie_datasets.datasets.tplinker.load import TPLinkerSplit
from ie_datasets.datasets.tplinker.webnlg.load import (
    load_tplinker_webnlg_schema,
    load_tplinker_webnlg_units,
)


def get_tplinker_webnlg_summary() -> str:
    lines: list[str] = []

    lines.append("=" * 80)
    schema = load_tplinker_webnlg_schema()

    lines.append(f"RELATION TYPES: {schema.num_relation_types} types")
    for relation_type in schema.relation_types:
        lines.append(f"  {relation_type.id:3d}: {relation_type.name}")

    for split in TPLinkerSplit:
        lines.append("=" * 80)
        units = list(load_tplinker_webnlg_units(split))
        lines.append(f"{split}: {len(units)} units")
        if split != "train":
            L = max(len(unit.id) for unit in units)
            for unit in units:
                lines.append(f"  {unit.id.rjust(L)}: {unit.num_chars:3d} chars, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")

    return "\n".join(lines)


__all__ = [
    "get_tplinker_webnlg_summary",
]

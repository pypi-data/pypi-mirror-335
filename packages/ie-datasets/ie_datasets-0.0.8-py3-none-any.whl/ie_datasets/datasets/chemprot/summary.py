from ie_datasets.datasets.chemprot.load import (
    ChemProtSplit,
    load_chemprot_units,
)


def get_chemprot_summary() -> str:
    lines: list[str] = []

    for split in ChemProtSplit:
        units = list(load_chemprot_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        L = max(len(str(unit.pmid)) for unit in units)
        for unit in units:
            lines.append(f"  {str(unit.pmid).rjust(L)}: {unit.num_chars:4d} chars, {unit.num_entity_mentions:3d} entity mentions, {unit.num_relations:2d} relations")

    return "\n".join(lines)


__all__ = [
    "get_chemprot_summary"
]

from ie_datasets.datasets.deft.load import (
    DEFTCategory,
    DEFTSplit,
    load_deft_units,
)


def get_deft_summary() -> str:
    lines: list[str] = []

    for split in DEFTSplit:
        for category in DEFTCategory:
            units = list(load_deft_units(split=split, category=category))

            lines.append("=" * 80)
            lines.append(f"{split}/{category}: {len(units)} units")

            L = max(len(str(unit.id)) for unit in units)

            for unit in units:
                lines.append(f"  {str(unit.id).rjust(L)}: {unit.num_chars:4d} chars, {unit.num_entities:2d} entities, {unit.num_relations:1d} relations")

    return "\n".join(lines)


__all__ = [
    "get_deft_summary"
]

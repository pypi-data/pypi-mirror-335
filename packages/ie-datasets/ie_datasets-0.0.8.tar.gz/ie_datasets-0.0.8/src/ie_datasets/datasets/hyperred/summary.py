from ie_datasets.datasets.hyperred.load import (
    HyperREDSplit,
    load_hyperred_units,
)


def get_hyperred_summary() -> str:
    lines: list[str] = []

    for split in HyperREDSplit:
        units = list(load_hyperred_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        if split != "train":
            for i, unit in enumerate(units):
                lines.append(f"  {i:4d}: {unit.num_tokens:3d} tokens, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")

    return "\n".join(lines)


__all__ = [
    "get_hyperred_summary",
]

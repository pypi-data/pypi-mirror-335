from ie_datasets.datasets.knowledgenet.load import (
    KnowledgeNetSplit,
    load_knowledgenet_units,
)


def get_knowledgenet_summary() -> str:
    lines: list[str] = []

    for split in KnowledgeNetSplit:
        units = list(load_knowledgenet_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        for i, unit in enumerate(units):
            lines.append(f"  {i:4d}: {unit.num_chars:4d} chars, {unit.num_passages:1d} passages, {unit.num_facts:2d} facts")

    return "\n".join(lines)


__all__ = [
    "get_knowledgenet_summary",
]

from ie_datasets.datasets.scirex.load import load_scirex_units, SciREXSplit


def get_scirex_summary() -> str:
    lines: list[str] = []

    for split in SciREXSplit:
        units = list(load_scirex_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        L = max(len(unit.doc_id) for unit in units)
        for unit in units:
            lines.append(f"  {unit.doc_id.rjust(L)}: {unit.num_words:5d} words, {unit.num_sentences:3d} sentences, {unit.num_entity_mentions:3d} entity mentions, {unit.num_relations:2d} relations")

    return "\n".join(lines)


__all__ = [
    "get_scirex_summary",
]

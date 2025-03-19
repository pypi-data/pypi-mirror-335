from ie_datasets.datasets.scierc.load import load_scierc_units, SciERCSplit


def get_scierc_summary() -> str:
    lines: list[str] = []

    for split in SciERCSplit:
        units = list(load_scierc_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        L = max(len(unit.doc_key) for unit in units)
        for unit in units:
            lines.append(f"  {unit.doc_key.rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_sentences:2d} sentences, {unit.num_entity_mentions:2d} entity mentions, {unit.num_relations:2d} relations")

    return "\n".join(lines)


__all__ = [
    "get_scierc_summary",
]

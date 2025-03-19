from ie_datasets.datasets.biored.load import BioREDSplit, load_biored_units


def get_biored_summary() -> str:
    lines: list[str] = []

    for split in BioREDSplit:
        units = list(load_biored_units(split))

        lines.append("=" * 80)
        lines.append(f"{split}: {len(units)} units")

        L = max(len(unit.id) for unit in units)
        for unit in units:
            lines.append(f"  {unit.id.rjust(L)}: {unit.num_chars:4d} chars, {unit.num_entity_mentions:2d} entity mentions, {unit.num_entities:2d} entities, {unit.num_relations:3d} relations")

    return "\n".join(lines)

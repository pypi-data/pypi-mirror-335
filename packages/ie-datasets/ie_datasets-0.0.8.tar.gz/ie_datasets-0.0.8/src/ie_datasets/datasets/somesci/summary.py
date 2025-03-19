from typing import Optional, Union

from ie_datasets.datasets.somesci.load import (
    load_somesci_schema,
    load_somesci_units,
    SoMeSciGroup,
    SoMeSciSplit,
    SoMeSciVersion,
)


def get_somesci_summary(
        version: Optional[Union[SoMeSciVersion, str]] = None,
) -> str:
    lines: list[str] = []

    schema = load_somesci_schema(version=version)
    lines.append("=" * 80)
    lines.append("SCHEMA")
    lines.append("-" * 80)
    lines.append(f"ENTITY TYPES: {len(schema.entity_types)} types")
    for t in schema.entity_types:
        lines.append(f"  {t.name}")
    lines.append("-" * 80)
    lines.append(f"RELATION TYPES: {len(schema.relation_types)} types")
    for t in schema.relation_types:
        lines.append(f"  {t.name}(")
        lines.append(f"    {'|'.join(t.argument_1_types)},")
        lines.append(f"    {'|'.join(t.argument_2_types)}")
        lines.append(f"  )")

    for group in SoMeSciGroup:
        for split in SoMeSciSplit:
            units = list(load_somesci_units(split, version=version, group=group))
            lines.append("=" * 80)
            lines.append(f"{split}/{group}: {len(units)} units")
            L = max(0 if unit.id is None else len(unit.id) for unit in units)
            for unit in units:
                id = "" if unit.id is None else unit.id
                lines.append(f"  {id.rjust(L)}: {unit.num_chars:6d} chars, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")

    return "\n".join(lines)


__all__ = [
    "get_somesci_summary",
]

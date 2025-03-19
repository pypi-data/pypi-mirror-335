from collections import defaultdict
from ie_datasets.datasets.crossre.load import (
    CrossREDomain,
    CrossRESplit,
    load_crossre_units,
)
from ie_datasets.datasets.crossre.unit import (
    CrossREEntityTypeName,
    CrossRERelationTypeName,
)


def get_crossre_summary() -> str:
    schema_lines: list[str] = []
    units_lines: list[str] = []

    entity_type_stats: dict[CrossREEntityTypeName, int] = defaultdict(int)
    relation_type_stats: dict[
        CrossRERelationTypeName,
        dict[str, dict[tuple[CrossREEntityTypeName, CrossREEntityTypeName], int]]
    ] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for split in CrossRESplit:
        for domain in CrossREDomain:
            units = list(load_crossre_units(split, domain=domain))

            units_lines.append("=" * 80)
            units_lines.append(f"{split}/{domain}: {len(units)} units")

            L = max(len(str(unit.doc_key)) for unit in units)

            for unit in units:
                units_lines.append(f"  {str(unit.doc_key).rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")
                for e in unit.entity_objects:
                    entity_type_stats[e.entity_type] += 1
                for r in unit.relation_objects:
                    key = r.relation_type if r.explanation == "" else r.explanation
                    head_span = (r.head_start, r.head_end)
                    tail_span = (r.tail_start, r.tail_end)
                    head_type = unit.entities_by_span[head_span].entity_type
                    tail_type = unit.entities_by_span[tail_span].entity_type
                    relation_type_stats[r.relation_type][key][(head_type, tail_type)] += 1

    schema_lines.append("=" * 80)
    schema_lines.append("SCHEMA")

    schema_lines.append("-" * 80)
    schema_lines.append(f"{len(entity_type_stats)} entity types")
    L = max(len(et) for et in entity_type_stats.keys())
    for et in CrossREEntityTypeName:
        count = entity_type_stats[et]
        schema_lines.append(f"  {et.rjust(L)}: {count}")

    schema_lines.append("-" * 80)
    relation_types = sorted(relation_type_stats.keys())
    schema_lines.append(f"{len(relation_types)} relation types")
    for rt in CrossRERelationTypeName:
        total = sum(
            sum(explanation_stats.values())
            for explanation_stats in relation_type_stats[rt].values()
        )
        schema_lines.append(f"  {rt}: {total}")
        explanation_stats = relation_type_stats[rt]
        explanations = sorted(explanation_stats.keys())
        for explanation in explanations:
            head_tail_stats = explanation_stats[explanation]
            total = sum(head_tail_stats.values())
            schema_lines.append(f"    {explanation}: {total}")
            for (head_type, tail_type), count in sorted(
                head_tail_stats.items(),
                key=lambda x: x[1],
                reverse=True,
            ):
                schema_lines.append(f"      {head_type} -> {tail_type}: {count}")

    return "\n".join(schema_lines + units_lines)


__all__ = [
    "get_crossre_summary",
]

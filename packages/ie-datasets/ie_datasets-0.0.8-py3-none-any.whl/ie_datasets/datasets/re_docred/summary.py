from collections import defaultdict

from ie_datasets.datasets.docred.schema import (
    DocREDEntityTypeID,
    DocREDRelationTypeID,
)
from ie_datasets.datasets.re_docred.load import (
    load_redocred_schema,
    load_redocred_units,
    ReDocREDSplit,
)


def get_redocred_summary() -> str:
    schema_lines: list[str] = []
    unit_lines: list[str] = []

    entity_type_counts_per_entity: dict[DocREDEntityTypeID, int] = defaultdict(int)
    entity_type_counts_per_mention: dict[DocREDEntityTypeID, int] = defaultdict(int)
    relation_type_stats: dict[
        DocREDRelationTypeID,
        dict[tuple[DocREDEntityTypeID, DocREDEntityTypeID], int],
    ] = defaultdict(lambda: defaultdict(int))

    for split in ReDocREDSplit:
        units = list(load_redocred_units(split=split))

        unit_lines.append("=" * 80)
        unit_lines.append(f"{split}: {len(units)} units")

        L = max(len(str(unit.title)) for unit in units)
        for unit in units:
            for entity_mentions in unit.vertex_set:
                for mention in entity_mentions:
                    entity_type_counts_per_mention[mention.type] += 1
                entity_types = set(v.type for v in entity_mentions)
                if len(entity_types) > 1:
                    print(unit.model_dump_json())
                for entity_type in entity_types:
                    entity_type_counts_per_entity[entity_type] += 1
            if unit.labels is not None:
                for relation in unit.labels:
                    head_types = set(v.type for v in unit.vertex_set[relation.h])
                    tail_types = set(v.type for v in unit.vertex_set[relation.t])
                    for head_type in head_types:
                        for tail_type in tail_types:
                            relation_type_stats[relation.r][(head_type, tail_type)] += 1

            unit_lines.append(f"  {str(unit.title).rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_sentences:2d} sentences, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")

    schema = load_redocred_schema()

    schema_lines.append("=" * 80)
    schema_lines.append("SCHEMA")

    schema_lines.append("-" * 80)
    schema_lines.append(f"{len(DocREDEntityTypeID)} entity types")
    L = max(len(entity_type) for entity_type in DocREDEntityTypeID)
    for entity_type in DocREDEntityTypeID:
        count_per_entity = entity_type_counts_per_entity[entity_type]
        count_per_mention = entity_type_counts_per_mention[entity_type]
        schema_lines.append(f"  {entity_type.rjust(L)}: {count_per_entity:5d} entities, {count_per_mention:5d} mentions")

    schema_lines.append("-" * 80)
    schema_lines.append(f"{len(DocREDRelationTypeID)} relation types")
    for relation_type in schema.relation_types:
        schema_lines.append(f"  {relation_type.id}: {relation_type.description}")
        counts = sorted((
            (count, h, t)
            for (h, t), count in relation_type_stats[relation_type.id].items()
        ), reverse=True)
        for count, head_type, tail_type in counts:
            schema_lines.append(f"    {head_type.rjust(L)} -> {tail_type.ljust(L)}: {count}")

    return "\n".join(schema_lines + unit_lines)


__all__ = [
    "get_redocred_summary"
]

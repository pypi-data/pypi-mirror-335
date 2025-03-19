from collections import defaultdict

from ie_datasets.datasets.docred.schema import (
    DocREDEntityTypeID,
    DocREDRelationTypeID,
)
from ie_datasets.datasets.docred.load import (
    DocREDSplit,
    load_docred_schema,
    load_docred_units,
)


def get_docred_summary() -> str:
    schema_lines: list[str] = []
    unit_lines: list[str] = []

    entity_type_counts_per_entity: dict[DocREDEntityTypeID, int] = defaultdict(int)
    entity_type_counts_per_mention: dict[DocREDEntityTypeID, int] = defaultdict(int)
    relation_type_stats: dict[
        DocREDRelationTypeID,
        dict[tuple[DocREDEntityTypeID, DocREDEntityTypeID], int],
    ] = defaultdict(lambda: defaultdict(int))

    for split in DocREDSplit:
        units = list(load_docred_units(split))

        unit_lines.append("=" * 80)
        unit_lines.append(f"{split}: {len(units)} units")

        L = max(len(unit.title) for unit in units)

        for unit in units:
            for entity_mentions in unit.vertex_set:
                for mention in entity_mentions:
                    entity_type_counts_per_mention[mention.type] += 1
                entity_types = set(v.type for v in entity_mentions)
                for entity_type in entity_types:
                    entity_type_counts_per_entity[entity_type] += 1
            if unit.labels is not None:
                for relation in unit.labels:
                    head_types = set(v.type for v in unit.vertex_set[relation.h])
                    tail_types = set(v.type for v in unit.vertex_set[relation.t])
                    for head_type in head_types:
                        for tail_type in tail_types:
                            relation_type_stats[relation.r][(head_type, tail_type)] += 1

            if split != "train_distant":
                if unit.is_labelled:
                    unit_lines.append(f"  {unit.title.rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_sentences:2d} sentences, {unit.num_entities:2d} entities, {unit.num_relations:2d} relations")
                else:
                    unit_lines.append(f"  {unit.title.rjust(L)}: {unit.num_tokens:3d} tokens, {unit.num_sentences:2d} sentences, {unit.num_entities:2d} entities")

    schema = load_docred_schema()

    schema_lines.append("=" * 80)
    schema_lines.append("SCHEMA")

    schema_lines.append("-" * 80)
    schema_lines.append(f"{len(DocREDEntityTypeID)} entity types")
    L = max(len(entity_type) for entity_type in DocREDEntityTypeID)
    for entity_type in DocREDEntityTypeID:
        count_per_entity = entity_type_counts_per_entity[entity_type]
        count_per_mention = entity_type_counts_per_mention[entity_type]
        schema_lines.append(f"  {entity_type.rjust(L)}: {count_per_entity:6d} entities, {count_per_mention:6d} mentions")

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
    "get_docred_summary"
]

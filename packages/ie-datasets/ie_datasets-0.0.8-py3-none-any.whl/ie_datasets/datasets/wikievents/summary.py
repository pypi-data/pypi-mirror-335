from collections import Counter, defaultdict

from ie_datasets.datasets.wikievents.load import (
    load_wikievents_ontology,
    load_wikievents_units,
    WikiEventsSplit,
)


def get_wikievents_summary() -> str:
    ontology_lines: list[str] = []
    unit_lines: list[str] = []


    ontology = load_wikievents_ontology()

    role_cardinality_by_event_type: dict[str, dict[str, tuple[int, int]]] = defaultdict(dict)
    for split in WikiEventsSplit:
        units = list(load_wikievents_units(split))
        unit_lines.append("=" * 80)
        unit_lines.append(f"{split}: {len(units)} units")
        L = max(len(unit.doc_id) for unit in units)
        for unit in units:
            for event_mention in unit.event_mentions:
                event_type = ontology.event_types_by_name[event_mention.event_type]

                role_counts = Counter(argument.role for argument in event_mention.arguments)
                role_cardinality = role_cardinality_by_event_type[event_mention.event_type]
                for role in event_type.roles:
                    count = role_counts[role]
                    if role in role_cardinality:
                        (lower, upper) = role_cardinality[role]
                        bounds = (min(lower, count), max(upper, count))
                    else:
                        bounds = (count, count)
                    role_cardinality[role] = bounds

                nargs = len(event_mention.arguments)
                if "*" in role_cardinality:
                    (lower, upper) = role_cardinality["*"]
                    bounds = (min(lower, nargs), max(upper, nargs))
                else:
                    bounds = (nargs, nargs)
                role_cardinality["*"] = bounds

            unit_lines.append(f"  {unit.doc_id.rjust(L)}: {unit.num_chars:5d} chars, {unit.num_tokens:5d} tokens, {unit.num_sentences:3d} sentences, {unit.num_entity_mentions:4d} entity mentions, {unit.num_event_mentions:3d} event mentions")
            ontology.validate_unit(unit)

    ontology_lines.append("=" * 80)
    ontology_lines.append("ONTOLOGY")
    ontology_lines.append("-" * 80)
    ontology_lines.append("ENTITY TYPES")
    L = max(len(entity_type.name) for entity_type in ontology.entity_types)
    for entity_type in ontology.entity_types:
        ontology_lines.append(f"  {entity_type.name.rjust(L)}: \"{entity_type.definition}\"")
    ontology_lines.append("-" * 80)
    ontology_lines.append("EVENT TYPES")
    for event_type in ontology.event_types:
        ontology_lines.append(f"  {event_type.name}: \"{event_type.template}\"")
        role_cardinality = role_cardinality_by_event_type[event_type.name]
        for role, (lower, upper) in sorted(role_cardinality.items()):
            ontology_lines.append(f"    {role}: {lower}-{upper}")

    return "\n".join(ontology_lines + unit_lines)


__all__ = [
    "get_wikievents_summary",
]

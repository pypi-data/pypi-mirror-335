from enum import StrEnum
import json
import os
from typing import Iterable, Union

from ie_datasets.datasets.wikievents.ontology import WikiEventsOntology
from ie_datasets.datasets.wikievents.unit import WikiEventsUnit
from ie_datasets.util.env import get_cache_dir
from ie_datasets.util.wget import open_or_wget


class WikiEventsSplit(StrEnum):
    TRAIN = "train"
    DEV = "dev"
    TEST = "test"


def load_wikievents_ontology() -> WikiEventsOntology:
    BASE_WIKIEVENTS_DIR = get_cache_dir(subpath="wikievents")

    ontology_path = os.path.join(BASE_WIKIEVENTS_DIR, "ontology.json")

    if os.path.exists(ontology_path):
        with open(ontology_path, "r") as f:
            ontology = WikiEventsOntology.model_validate_json(f.read(), strict=True)

    else:
        ENTITY_TYPES_URL = "https://raw.githubusercontent.com/raspberryice/gen-arg/refs/heads/tapkey/ontology/entity_types.json"
        EVENT_TYPES_URL = "https://raw.githubusercontent.com/raspberryice/gen-arg/refs/heads/main/event_role_KAIROS.json"

        with open_or_wget(
            url=ENTITY_TYPES_URL,
            local_path=os.path.join(BASE_WIKIEVENTS_DIR, "raw/entity_types.json"),
        ) as entities_file:
            entities_json = json.load(entities_file)
            assert isinstance(entities_json, dict)

        with open_or_wget(
            url=EVENT_TYPES_URL,
            local_path=os.path.join(BASE_WIKIEVENTS_DIR, "raw/event_types.json"),
        ) as events_file:
            events_json = json.load(events_file)
            assert isinstance(events_json, dict)

        # fix error #1 (see README) in the entity types
        crime_entity_type = {
            "Type": "CRM",
            "Output Value for Type": "crm",
            "Definition": "An unlawful act punishable by a state or other authority.",
        }
        assert len(entities_json) == 24
        entities_json["24"] = crime_entity_type

        # fix errors #1,#2 (see README) in the event types
        for event_type in events_json.values():
            for role_types in event_type["role_types"]:
                for i in range(len(role_types)):
                    if role_types[i] == "event":
                        role_types[i] = "CRM"
                    if role_types[i] == "side":
                        role_types[i] = "SID"
                    assert len(role_types[i]) == 3

        # fix error #3 (see README)
        event = events_json["ArtifactExistence.DamageDestroyDisableDismantle.Dismantle"]
        assert event["event_id"] == "LDC_KAIROS_evt_004"
        assert event["template"] == "<arg1> dismantled <arg2> using <arg3> instrument in <arg4> place"
        event["template"] = "<arg1> dismantled <arg2> into <arg4> components using <arg3> instrument in <arg5> place"

        # capitalize all entity types
        for entity_type in entities_json.values():
            entity_type_id = entity_type["Type"]
            assert entity_type_id == entity_type_id.upper()
            assert entity_type["Output Value for Type"] == entity_type_id.lower()
            del entity_type["Output Value for Type"]
        for event_type in events_json.values():
            for role_types in event_type["role_types"]:
                for i in range(len(role_types)):
                    role_types[i] = role_types[i].upper()

        # adjust fields
        for entity_type in entities_json.values():
            entity_type["name"] = entity_type.pop("Type")
            entity_type["definition"] = entity_type.pop("Definition")
        for t, event_type in events_json.items():
            event_type.pop("i-label")
            assert "name" not in event_type
            event_type["name"] = t

        ontology = WikiEventsOntology.model_validate({
            "entity_types": list(entities_json.values()),
            "event_types": list(events_json.values()),
        }, strict=True)
        with open(ontology_path, "x") as f:
            f.write(ontology.model_dump_json())

    return ontology


def load_wikievents_units(
        split: Union[WikiEventsSplit, str],
) -> Iterable[WikiEventsUnit]:
    BASE_WIKIEVENTS_DIR = get_cache_dir(subpath="wikievents")

    split = WikiEventsSplit(split)

    split_path = os.path.join(BASE_WIKIEVENTS_DIR, f"{split}.jsonl")

    if os.path.exists(split_path):
        with open(split_path, "r") as f:
            for line in f:
                unit = WikiEventsUnit.model_validate_json(line, strict=True)
                yield unit

    else:
        DATASET_BASE_URL = "https://gen-arg-data.s3.us-east-2.amazonaws.com/wikievents/data"

        units: list[WikiEventsUnit] = []

        with (
            open_or_wget(
                url=f"{DATASET_BASE_URL}/{split}.jsonl",
                local_path=os.path.join(BASE_WIKIEVENTS_DIR, f"raw/{split}.jsonl"),
            ) as unit_file,
            open_or_wget(
                url=f"{DATASET_BASE_URL}/coref/{split}.jsonlines",
                local_path=os.path.join(BASE_WIKIEVENTS_DIR, f"raw/coref/{split}.jsonl"),
            ) as coref_file,
        ):
            for i, (unit_line, coref_line) in enumerate(zip(unit_file, coref_file, strict=True)):
                unit_json = json.loads(unit_line)
                coref_json = json.loads(coref_line)

                # fix error #4 (see README)
                if split is WikiEventsSplit.TRAIN and i == 89:
                    assert unit_json["doc_id"] == "33_VOA_EN_NW_2014.12.18.2564370"
                    entity_mention = unit_json["entity_mentions"][115]
                    assert entity_mention["id"] == "33_VOA_EN_NW_2014.12.18.2564370-T116"
                    assert entity_mention["text"] == "James Whitey Bulger"
                    entity_mention["text"] = 'James "Whitey" Bulger'

                for event_mention in unit_json["event_mentions"]:
                    # fix error #5 (see README)
                    if event_mention["event_type"] in (
                        "Contact.RequestCommand.Broadcast",
                        "Contact.RequestCommand.Correspondence",
                        "Contact.RequestCommand.Meet",
                    ):
                        event_mention["event_type"] = "Contact.RequestCommand.Unspecified"

                    # fix error #6 (see README)
                    elif event_mention["event_type"] in (
                        "Contact.ThreatenCoerce.Broadcast",
                        "Contact.ThreatenCoerce.Correspondence",
                    ):
                        event_mention["event_type"] = "Contact.ThreatenCoerce.Unspecified"

                # fix error #7 (see README)
                if split is WikiEventsSplit.TRAIN and i == 14:
                    assert unit_json["doc_id"] == "scenario_en_kairos_53"
                    event_mention = unit_json["event_mentions"][10]
                    assert event_mention["id"] == "scenario_en_kairos_53-E12", event_mention
                    arg0, arg1 = event_mention["arguments"]

                    assert arg0["entity_id"] == "scenario_en_kairos_53-T43"
                    assert arg0["role"] == "Observer"
                    arg0["role"] = "Investigator"

                    assert arg1["entity_id"] == "scenario_en_kairos_53-T46"
                    assert arg1["role"] == "ObservedEntity"
                    arg1["role"] = "Defendant"

                # fix error #8 (see README)
                if split is WikiEventsSplit.TRAIN and i == 92:
                    assert unit_json["doc_id"] == "wiki_ied_bombings_0"
                    event_mentions = unit_json["event_mentions"]
                    assert isinstance(event_mentions, list)
                    event_mention = event_mentions[54]
                    assert event_mention["id"] == "wiki_ied_bombings_0-E55"
                    assert event_mention["event_type"] == "Movement.Transportation.Unspecified"
                    event_mentions.pop(54)

                # all units have no relations so we just drop them
                assert unit_json["relation_mentions"] == []
                del unit_json["relation_mentions"]

                assert "coreferences" not in unit_json
                unit_json["coreferences"] = coref_json
                unit = WikiEventsUnit.model_validate_json(
                    json.dumps(unit_json),
                    strict=True,
                )
                units.append(unit)

        with open(split_path, "x") as f:
            for unit in units:
                f.write(unit.model_dump_json() + "\n")

        yield from units


__all__ = [
    "load_wikievents_ontology",
    "load_wikievents_units",
    "WikiEventsSplit",
]

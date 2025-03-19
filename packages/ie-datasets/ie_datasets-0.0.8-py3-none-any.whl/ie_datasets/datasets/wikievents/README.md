# WikiEvents [Event Argument Extraction]

**NAACL 2021**: [Document-Level Event Argument Extraction by Conditional Generation](https://aclanthology.org/2021.naacl-main.69/)

**GitHub**: [`raspberryice/gen-arg`](https://github.com/raspberryice/gen-arg)

**License**: [MIT](https://github.com/raspberryice/gen-arg/blob/main/LICENSE)

## Ontology

The paper authors mention that WikiEvents follows the KAIROS (Knowledge-directed Artificial Intelligence Reasoning Over Schemas) ontology without linking to the original source of the ontology.
However, they provide files that can be assumed to be some processed version of the KAIROS ontology.

- [entity type definitions](https://github.com/raspberryice/gen-arg/blob/tapkey/ontology/entity_types.json )
- [event types](https://github.com/raspberryice/gen-arg/blob/main/event_role_KAIROS.json)

## Quirks

- The start and end bounds of each token in the `sentences` field cannot be used on the `text` field.
  The offsets account for whitespace between sentences, which is deleted in the `text` field.
  Instead, the original text should be reconstructed by concatenating the tokens, with faithful amounts of whitespace inserted between them.
  We fix this with aggressive validation in the loading script.
- Coreferences are stored separately from the main annotations, despite their negligible size.
  For each unit, we merge the coreference data into the main data via an added `coreferences` field.
- Entity types are uppercase in the annotations and in the entity types schema, but they are lowercase in the event types schema when listed as role types.
  When loading the data, we standardize all entity types to uppercase.
- We convert all field names to standard Python snake case.
  We replace the reserved keyword `type` with `name` instead.
- We remove fields like `i-label` and `Output Value for Type` from the ontology, which have no useful meaning.

## Errata

We hard-code corrections to the following errata in the ontology:

1. The `event` role type corresponds to `CRM` in the actual annotations, but neither name appears in the entity type schema.
   We replace `event` with `CRM` for 3-lettered consistency, and add a description (copied from [Wikipedia](https://en.wikipedia.org/wiki/Crime)) for `CRM` as the 25th entity type:
   ```json
   {
     "Type": "CRM",
     "Output Value for Type": "crm",
     "Definition": "An unlawful act punishable by a state or other authority."
   }
   ```
   This also fixes the entity mention `scenario_en_37-T2` ("homicide"), which has the `CRM` entity type.
2. The `side` role type corresponds to `SID` in the actual annotations.
3. The event type `ArtifactExistence.DamageDestroyDisableDismantle.Dismantle` has an incorrect template with 5 roles (`Dismantler`, `Artifact`, `Instrument`, `Components`, `Place`), but only 4 arguments.
   We replace the template: `<arg1> dismantled <arg2> into <arg4> components using <arg3> instrument in <arg5> place`.

We hard-code corrections to the following errata in the events:

4. Entity mention `33_VOA_EN_NW_2014.12.18.2564370-T116` has the incorrect text `James Whitey Bulger` whereas the corresponding span is `James "Whitey" Bulger`.
5. The event types `Contact.RequestCommand.Broadcast`, `Contact.RequestCommand.Correspondence`, and `Contact.RequestCommand.Meet` appear 5, 1, and 3 times respectively in the data, but they are not listed in the ontology.
   We replace the annotations with `Contact.RequestCommand.Unspecified`, the most fitting alternative.
6. The event types `Contact.ThreatenCoerce.Broadcast` and `Contact.ThreatenCoerce.Correspondence` appear 5 and 3 times respectively in the data, but they are not listed in the ontology.
   We replace the annotations with `Contact.ThreatenCoerce.Unspecified`, the most fitting alternative.
7. The event mention `scenario_en_kairos_53-E12` is annotated with the wrong roles, which should be `Investigator` and `Defendant` instead of `Observer` and `ObservedEntity`, respectively.
8. The event mention `wiki_ied_bombings_0-E55` violates the schema by annotating a vehicle (`VEH`) with the role `Destination` of a `Movement.Transportation.Unspecified` event.
   This is the only role type violation in the dataset, so we delete it to avoid trouble.

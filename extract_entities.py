"""Extracts an entity's tokens and the token's number of occurrances
from an exported LUIS Application. Requires two parameters, the
name exported file and the entity you are looking for.

Currently supports hierarchical, prebuilt domain and simple entities.
Does not search in "composites", "closedLists", or "bing_entities"
for provided entity.

Example usage: python extract_entities.py MyFirstApp.json Weather.Location

Uses regex to match entities, this means if you provide the parent of
a hierarchical entity, the script will return all instances of just
the parent entity and all instances of its children.

E.g. providing "Fruits" will return Fruits, Fruits::Apples, Fruits::Citrus

To drill down to a specific hierarchical child, provide the full
child's name.

E.g. "Fruits::Apples" will return only Fruits::Apples

Tested with Python 3.6.2
"""

import json
import sys
import re

if len(sys.argv) < 3:
    raise RuntimeError('You must provide a json and an entity to search for.')

with open(sys.argv[1], 'r') as exported_model:
    if exported_model is None:
        raise RuntimeError('Json not found.')
    else:
        new_object = json.load(exported_model)

        entity_found = False
        for key in new_object['entities']:
            if entity_found is True:
                break
            if key['name'] == sys.argv[2]:
                print("Found entity in application's entities", sys.argv[2])
                entity_found = True

        utterances_with_entities = list()
        ENTITY_PATTERN = re.compile(sys.argv[2])

        if entity_found is True:
            UTTERANCES = new_object['utterances']
            for u in UTTERANCES:
                for entity in u['entities']:
                    if ENTITY_PATTERN.search(entity['entity']):
                        utterances_with_entities.append(u)
                        break
        else:
            raise RuntimeError('Entity not found.')

        just_entities = dict()
        if len(utterances_with_entities) > 0:
            for utterance in utterances_with_entities:
                text = utterance['text']
                instance_list = list()
                for entity in utterance['entities']:
                    if ENTITY_PATTERN.search(entity['entity']):
                        instance_list.append(entity)
                for entity in instance_list:
                    token = text[int(entity['startPos']):int(entity['endPos'])+1]
                    if token in just_entities:
                        just_entities[token] += 1
                    else:
                        just_entities[token] = 1

        OUTPUT_ENTITIES = sys.argv[2] + ".json"
        with open(OUTPUT_ENTITIES, 'w') as entity_output:
            try:
                json.dump(just_entities, entity_output)
                print(f'entities successfully saved. see "{OUTPUT_ENTITIES}"')
            except:
                raise RuntimeError('Unable to save entities.')

        OUTPUT_UTTERANCES = sys.argv[2] + "_utterances.json"
        with open(OUTPUT_UTTERANCES, 'w') as utterances_output:
            try:
                json.dump(utterances_with_entities, utterances_output)
                print(f'utterances successfully saved. see "{OUTPUT_UTTERANCES}"')
            except:
                raise RuntimeError('Unable to save utterances.')

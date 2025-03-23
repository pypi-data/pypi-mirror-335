import json
import os
from pathlib import Path

import instructor
import polib
from loguru import logger
from openai import OpenAI

client = instructor.from_openai(OpenAI())
default_locale = "en"

default_catalog_path = str(Path(__file__).parent / default_locale / "LC_MESSAGES" / "messages.po")
default_catalog = polib.pofile(default_catalog_path)

for entry in default_catalog:
    if not entry.msgstr:
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful translator helping me fill a string placeholder.",
            },
            {
                "role": "user",
                "content": f"Fill the following string:\n\n{entry.msgid}:",
            },
        ]
        tl = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_model=str,
            max_retries=3,
            temperature=0,
            top_p=0,
            seed=1234,
        )
        entry.msgstr = tl
        logger.warning(f"Translated {entry.msgid} to {entry.msgstr}")


# manual translations for demos - remove after
manuals = [
    ("Salesforce.Event.Poultry_age__c", "Age des poules (semaines)"),
    ("Salesforce.Event.Poultry_weight__c", "Poinds des poules (g)"),
    ("Salesforce.Event.Caliber__c", "Calibre (g)"),
    ("Salesforce.Event.Number_of_weighted_poultry__c", "Nombre de poules pesées"),
    ("Salesforce.Event.Egg_shell_quality__c", "Qualité de coquille"),
    ("Salesforce.Event.Homogeneity__c", "Homogénéité"),
    ("Salesforce.Event.Egg_laying__c", "Pourcentage de ponte"),
    ("Salesforce.Event.Mortality__c", "Mortalité"),
    ("Salesforce.Event.Food_consumption__c", "Consommation d'aliment (g)"),
    ("Salesforce.Event.Condition_of_feathering__c", "État de l-emplumement"),
    ("Salesforce.Event.Intervention_type__c", "Type d'intervention"),
    ("Salesforce.Event.Status_after_intervention__c", "Statut après intervention"),
    ("Salesforce.Event.Equipment_affected__c", "Équipement affecté"),
    ("Salesforce.Event.Severity__c", "Sévérité"),
    ("Salesforce.Event.Sujet_visite_generale__c", "Sujet"),
    ("Salesforce.Event.Type_visite_generale__c", "Type de visite"),
    ("Salesforce.Event.Product_satisfaction__c", "Satisfaction du produit"),
    ("Salesforce.Event.Service_satisfaction__c", "Satisfaction du service"),
]

for manual_key, manual_tl_fr in manuals:
    manual_entry = default_catalog.find(manual_key)
    if not manual_entry or not manual_entry.msgstr:
        messages = [
            {
                "role": "system",
                "content": f"You are a helpful translator helping me translate my website from fr to {default_locale}",
            },
            {
                "role": "user",
                "content": f"Translate the following string:\n\nId:{manual_key}\n\nContent:{manual_tl_fr}\n\nOnly return the content.",
            },
        ]
        tl = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            response_model=str,
            max_retries=3,
            temperature=0,
            top_p=0,
            seed=1234,
        )
        manual_entry = polib.POEntry(
            msgid=manual_key,
            msgstr=tl,
        )
        default_catalog.append(manual_entry)
default_catalog.save(default_catalog_path)

logger.info(f"Finished translating default locale saved to {default_catalog_path}")

for other_locale in Path(__file__).parent.iterdir():
    if other_locale.name == default_locale or not other_locale.is_dir() or not "LC_MESSAGES" in os.listdir(other_locale):
        continue

    logger.info(f"Checking {other_locale.name} ({other_locale})")
    other_local_path = other_locale / "LC_MESSAGES" / "messages.po"
    if not other_local_path.exists():
        po = polib.POFile()
        po.metadata = default_catalog.metadata
        po.save(other_local_path)
    other_catalog = polib.pofile(other_locale / "LC_MESSAGES" / "messages.po")

    for entry in default_catalog:
        other_entry = other_catalog.find(entry.msgid)
        if not other_entry or not other_entry.msgstr:
            logger.info(f"Translating {entry.msgid} from {default_locale} to {other_locale}")
            messages = [
                {
                    "role": "system",
                    "content": f"You are a helpful translator helping me translate my website from {default_locale} to {other_locale}.",
                },
                {
                    "role": "user",
                    "content": f"Translate the following string:\n\nId:{entry.msgid}\n\nContent:{entry.msgstr}\n\nOnly return the content.",
                },
            ]
            tl = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                response_model=str,
                max_retries=3,
                temperature=0,
                top_p=0,
                seed=1234,
            )
            other_entry = polib.POEntry(
                msgid=entry.msgid,
                msgstr=tl,
                occurrences=entry.occurrences,
            )
            other_catalog.append(other_entry)
    other_catalog.save(other_local_path)

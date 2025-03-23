from pathlib import Path

import polib
import requests
from simple_salesforce import SFType

from plurally.models.sf.base import set_locale
from plurally.models.sf.salesforce_crm import get_localization_key

access_token = "00DQy00000FlxqP!AQEAQPcSmW7CXCD4eoXIfSIlIzZWcZh4jDyadNtxkOkH8JY_tGaaqsZvQ1ePBA5F0cjn10s6ydXxJvLYMHisd145UhU1PAAE"
sf_instance = "plurally2-dev-ed.develop.my.salesforce.com"

set_locale("fr")

obj_types = ["Account", "Contact", "Opportunity", "Lead", "Event", "Task"]

for obj_type in obj_types:
    sftype = SFType(obj_type, session_id=access_token, sf_instance=sf_instance)
    for locale in ["en_US", "fr"]:
        set_locale(locale)
        lan = locale.split("_")[0]
        po_file_path = Path(f"plurally/localization/translations/{lan}/LC_MESSAGES/salesforce.po").absolute()
        if not po_file_path.exists():
            pof = polib.POFile()
            pof_copy_path = Path(f"plurally/localization/translations/{lan}/LC_MESSAGES/messages.po").absolute()
            if not pof_copy_path.exists():
                raise FileNotFoundError(f"File not found: {pof_copy_path} - needed for copying metadata")
            pof.metadata = polib.pofile(str(pof_copy_path)).metadata
            pof.save(str(po_file_path))

        pof = polib.pofile(str(po_file_path))

        x = sftype.describe()
        obj_type_entry = polib.POEntry(msgid=get_localization_key(obj_type), msgstr=x["label"])
        if obj_type_entry not in pof:
            pof.append(obj_type_entry)
        for field in x["fields"]:
            entry = polib.POEntry(msgid=get_localization_key(obj_type, field["name"]), msgstr=field["label"])
            if entry in pof:
                continue
            pof.append(entry)
        pof.save(str(po_file_path))


set_locale("fr")

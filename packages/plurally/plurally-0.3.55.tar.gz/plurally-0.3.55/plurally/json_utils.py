import json
from datetime import datetime

import jsonref


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# Custom hook to decode datetime strings
def datetime_decoder(dct):
    for key, value in dct.items():
        try:
            # Try to parse the value as ISO 8601 date format
            dct[key] = datetime.fromisoformat(value)
        except (ValueError, TypeError):
            # If parsing fails, keep the value as is
            pass
    return dct


# super hacky
def dump_to_json_dict(data):
    return json.loads(json.dumps(data, cls=DateTimeEncoder))


def load_from_json_dict(data):
    return json.loads(json.dumps(data), object_hook=datetime_decoder)


def replace_refs(schema):
    schema = jsonref.replace_refs(schema, proxies=False, merge_props=True)
    return schema

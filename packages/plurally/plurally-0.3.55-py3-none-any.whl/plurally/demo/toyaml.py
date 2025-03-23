import json
import sys
from pathlib import Path

import ruamel.yaml as yaml


def json_to_yaml_with_multiline(input_json):
    def multiline_representer(dumper, data):
        """Custom representer to handle multiline strings with |."""
        if "\n" in data:  # Check if the string contains newlines
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, multiline_representer)

    # Convert JSON to Python dictionary
    data = json.loads(input_json)

    # Convert Python dictionary to YAML
    yaml_output = yaml.dump(data, allow_unicode=True)
    return yaml_output


in_path = Path(sys.argv[1])
input_json = in_path.read_text()

yaml_output = json_to_yaml_with_multiline(input_json)

out_path = in_path.with_suffix(".yaml")
out_path.write_text(yaml_output)

print(f"Converted {in_path} to {out_path}")

in_path.unlink()  # Remove the original JSON file



from pathlib import Path
from pprint import pprint

import yaml

def load_demos():
    demos = {}
    for flow_yaml in (Path(__file__).parent / "flows").glob("*.yaml"):
        demos[flow_yaml.stem] = yaml.safe_load(flow_yaml.read_text())
    return demos




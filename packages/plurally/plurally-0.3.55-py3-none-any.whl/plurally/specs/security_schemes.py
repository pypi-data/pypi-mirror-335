from copy import deepcopy
from pathlib import Path

import yaml

SECURITY_SCHEMES = yaml.safe_load((Path(__file__).parent / "security_schemes.yaml").read_text())


def get_security_schemes():
    return deepcopy(SECURITY_SCHEMES)

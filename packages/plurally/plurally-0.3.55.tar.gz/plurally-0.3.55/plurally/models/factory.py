from plurally import models
from plurally.models import subflow

MAP = {}
for group_name, module in models.GROUPS:
    for kls_name in module.__all__:
        kls = getattr(module, kls_name)
        MAP[kls_name] = (kls, kls.InitSchema, group_name)
MAP["Subflow"] = (subflow.Subflow, subflow.Subflow.InitSchema, None)


def create_node(**json_payload):
    node_kls = json_payload.pop("kls")
    return MAP[node_kls][0].parse(**json_payload)

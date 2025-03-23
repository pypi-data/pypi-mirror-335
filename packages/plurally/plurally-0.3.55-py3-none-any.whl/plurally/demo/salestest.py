import json
import os
from datetime import datetime
from pathlib import Path
from pprint import pprint

import yaml

from plurally.models.action.transcript import Transcript
from plurally.models.flow import Flow
from plurally.models.form import Form, FormEntry, FormEntryType
from plurally.models.output.text import TextOutput


def _get_trigger_type(flow):
    nodes = [node for node in flow.get_flatten_graph().nodes if node.is_trigger]
    if not nodes:
        return None
    return nodes[0]


def load_model(path):
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        data = yaml.unsafe_load(path.read_text())

    flow = Flow.parse(data["flow_json"])

    # get form node
    form_node = _get_trigger_type(flow)

    graph = flow.get_flatten_graph()
    # get transcript node
    transcript_node = list(graph.out_edges(form_node, data=True))[0][1]
    assert isinstance(transcript_node, Transcript)

    # delete form node
    flow.delete_node(form_node.node_id)
    flow.delete_node(transcript_node.node_id)

    # add new form node
    form_node = flow.add_node(
        Form(
            Form.InitSchema(
                name="Form",
                form=[
                    FormEntry(
                        name="transcript",
                        type=FormEntryType.TEXT,
                    )
                ],
            )
        )
    )
    for _, transcript_node_target, keys in graph.out_edges(transcript_node, data=True):
        flow.connect_nodes(form_node, "transcript", transcript_node_target, keys["tgt_handle"])
    assert flow.is_valid(), flow.get_issues()
    return flow, form_node


def run_model(model_path, transcript):
    flow, form_node, *_ = load_model(model_path)
    results = flow(output_overrides={form_node.node_id: {"transcript": transcript}})
    return results


def main():
    load_env()
    model_path = Path("/home/villqrd/repos/plurally-engine/demo/flows/FlowNoCommit.yaml")
    print(model_path.name)
    print(model_path.name)
    print(model_path.name)
    transcript = "Je sors d'un rendez-vous de 30 minutes avec Stéphanie Keller, directrice générale de hy-line, une entreprise de 35 employés avec un chiffre d'affaires de 2,5 millions par an. Elle a exprimé son intérêt pour la livraison le 15 mars de 2400 poules pondeuses pour un total d'environ 5000 euros. Il faut qu'on prépare un contrat pour vendredi et qu'on refasse un rendez-vous avec Stéphanie en personne et Olivier Lucien, son directeur technique, mercredi de la semaine prochaine."
    # transcript = "Ok, je sors d'un nouveau rendez-vous chez iLine où j'ai rencontré Stéphanie et Olivier, Lucien Directeur de poulailler. On a identifié une nouvelle opportunité de 3300 poules pondeuses de catégorie 133. C'est pour 10000 euros et date de livraison le 6 juin."
    output = run_model(model_path, transcript)
    pprint(output.model_dump())


def load_env():
    iso_dt = datetime(2024, 12, 22, 10, 0, 0).isoformat()
    os.environ["PLURALLY_START_ISO_TIMESTAMP"] = iso_dt
    os.environ["PLURALLY_SMTP_SERVER"] = "mail.postale.io"
    os.environ["PLURALLY_SMTP_PORT"] = "587"
    os.environ["PLURALLY_SMTP_USERNAME"] = "hello@tryplurally.com"
    os.environ["PLURALLY_OUTPUT_LANGUAGE"] = "French"
    os.environ["PLURALLY_TOKEN_URL"] = "https://apidev.tryplurally.com/api/v1/auth/token"
    os.environ["PLURALLY_API_KEY"] = "nE0btr8_QdHinhqw9hQZTIbToEQAy_dSWT-FHa7XYik"
    os.environ["PLURALLY_COMMIT_MODE"] = "no_commit"
    os.environ["JSON_PATH_DEBUG"] = "/home/villqrd/repos/plurally-engine/debug.json"


if __name__ == "__main__":
    main()

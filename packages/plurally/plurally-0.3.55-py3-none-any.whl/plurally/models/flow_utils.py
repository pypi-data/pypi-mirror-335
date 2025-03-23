from collections import defaultdict
from copy import deepcopy

import networkx as nx
from loguru import logger

from plurally.models import factory
from plurally.models.auto import Auto
from plurally.models.meta import InstagramNewDm, InstagramSendDm
from plurally.models.node import Node
from plurally.models.subflow import Subflow
from plurally.models.utils import is_list_type


def get_annots_or_raise(node, handle, schema):
    if handle not in schema.model_fields:
        raise ValueError(f"Handle {handle} not found in node {node}, options are {list(schema.model_fields)}")
    return schema.model_fields[handle]


def connect_nodes(graph, src_node: Node, src_handle: str, tgt_node: Node, tgt_handle: str):
    if src_node is tgt_node:
        raise ValueError(f"Cannot connect node with itself: {src_node}")

    for node in (src_node, tgt_node):
        if node not in graph:
            raise ValueError(f"{node} was not added to {graph} before connecting" f" {src_handle} to {tgt_handle}")

    outputs_annots = get_annots_or_raise(src_node, src_handle, src_node.OutputSchema)
    if outputs_annots.annotation is Auto:
        # if there already is a connection, raise
        for src, tgt, key in graph.out_edges(src_node, data=True):
            if key["src_handle"] == src_handle:
                raise ValueError("Auto outputs cannot be connected multiple times")
    inputs_annots = get_annots_or_raise(tgt_node, tgt_handle, tgt_node.InputSchema)
    # if tgt_handle is not a list and there already is a connection it is False
    if not is_list_type(inputs_annots):
        for src, tgt, key in graph.in_edges(tgt_node, data=True):
            if key["tgt_handle"] == tgt_handle:
                raise ValueError(f"Node {tgt_node.name} already has a connection for {tgt_handle}")

    if not tgt_node.validate_connection(src_node, src_handle, tgt_handle):
        # output_node_schema = src_node.OutputSchema.model_fields.get(src_handle)
        # input_node_schema = tgt_node.InputSchema.model_fields.get(tgt_handle)
        # assert False, (output_node_schema.annotation.model_fields, input_node_schema.annotation.model_fields)
        logger.debug(f"Failed to connect {src_node.name=} {src_handle=} {tgt_node=} {tgt_handle=}")
        err_msg = f"Connection impossible, types are not compatible: {src_handle} -> {tgt_handle}"
        # if inputs_annots.annotation
        #     err_msg += f"\n\nTry changing {src_handle} to {HANDLE_TYPE_FRIENDLY[HandleType.AUTO.value]}"
        raise ValueError(err_msg)

    key = f"{src_handle}###{tgt_handle}"
    if (src_node, tgt_node, key) in graph.edges:
        raise ValueError(f"Connection between {src_node} and {tgt_node} with {src_handle=} and {tgt_handle=} already exists")

    graph.add_edge(
        src_node,
        tgt_node,
        src_handle=src_handle,
        tgt_handle=tgt_handle,
        key=key,
    )


def disconnect_all_nodes_connected_to(graph, node_id: str, handle: str = None, mode: str = "all"):
    assert mode in ("all", "source", "target")
    to_remove = []

    for src_node, tgt_node, key in graph.edges:
        src_handle, tgt_handle = key.split("###")

        is_src = (src_node.node_id == node_id or node_id in src_handle) and (
            not handle or src_handle == handle or src_handle.endswith(f".{handle}")
        )
        is_tgt = (tgt_node.node_id == node_id or node_id in tgt_handle) and (
            not handle or tgt_handle == handle or tgt_handle.endswith(f".{handle}")
        )

        if mode == "all":
            if is_src or is_tgt:
                to_remove.append((src_node, tgt_node, key))
        elif mode == "target" and is_tgt:
            to_remove.append((src_node, tgt_node, key))
        elif mode == "source" and is_src:
            to_remove.append((src_node, tgt_node, key))

    for node in graph.nodes:
        if isinstance(node, Subflow):
            disconnect_all_nodes_connected_to(node.graph, node_id, handle, mode)

    for src_node, tgt_node, key in to_remove:
        graph.remove_edge(src_node, tgt_node, key=key)


def _automate_email_replyto_connection(out_graph):
    needed_connections = [
        ("subject", "previous_email_subject_"),
        ("content", "previous_email_body_"),
        ("datetime_received", "previous_email_datetime_received_"),
        ("sender_name", "previous_email_sender_name_"),
        ("sender_email", "previous_email_sender_email_"),
    ]

    add_connections = []
    for src, tgt, data in out_graph.edges(data=True):
        if data["tgt_handle"] == "reply_to":
            for src_handle, tgt_handle in needed_connections:
                add_connections.append((src, src_handle, tgt, tgt_handle))
    for connection in add_connections:
        connect_nodes(out_graph, *connection)


def _automate_insta_escalation_connection(out_graph):
    needed_connections = [
        ("was_escalated_previously_", "was_escalated_previously_"),
    ]
    new_dm_nodes = []
    send_dm_nodes = []
    for node in out_graph.nodes:
        if isinstance(node, InstagramNewDm):
            new_dm_nodes.append(node)
        elif isinstance(node, InstagramSendDm):
            send_dm_nodes.append(node)
    if send_dm_nodes:
        assert len(send_dm_nodes) == 1, f"Only one InstagramSendDm block is allowed, found {len(send_dm_nodes)}"
        if len(new_dm_nodes) == 1:
            # check if there are required connections
            for needed_src, needed_tgt in needed_connections:
                for src, _, data in out_graph.in_edges(send_dm_nodes[0], data=True):
                    if src == new_dm_nodes[0] and data["src_handle"] == needed_src and data["tgt_handle"] == needed_tgt:
                        break
                else:
                    connect_nodes(
                        out_graph,
                        new_dm_nodes[0],
                        needed_src,
                        send_dm_nodes[0],
                        needed_tgt,
                    )


def get_flatten_graph(in_graph):
    out_graph = nx.MultiDiGraph()

    edges = set()
    for node in in_graph.nodes:
        if isinstance(node, Subflow):
            out_graph = nx.compose(out_graph, node.graph)
        else:
            out_graph.add_node(node)

    for src, tgt, data in in_graph.edges(data=True):
        tgt_handle = data["tgt_handle"]
        src_handle = data["src_handle"]

        if isinstance(src, Subflow):
            src_id, src_handle = src_handle.split(".")
            src = src.get_node(src_id)

        if isinstance(tgt, Subflow):
            if "." in tgt_handle:
                tgt_id, tgt_handle = tgt_handle.split(".")
                tgt = tgt.get_node(tgt_id)
            else:
                assert tgt_handle == "run"
                # add virtual edges to each subnode.run handle
                for subnode in tgt.graph.nodes:
                    edges.add((src, src_handle, subnode, "run"))
                # do not add the one to the run handle of subflow
                # because subflow won't be in flatten graph
                continue
        edges.add((src, src_handle, tgt, tgt_handle))
    # we could skip checks here and make things faster if necessary
    for src, src_handle, tgt, tgt_handle in edges:
        connect_nodes(
            out_graph,
            src,
            src_handle,
            tgt,
            tgt_handle,
        )

    _automate_insta_escalation_connection(out_graph)
    _automate_email_replyto_connection(out_graph)
    return out_graph


def ungroup_subflow_data(flow_serialized, node_id):
    nodes_to_add = []
    edges_to_add = []
    node_ids = []
    for ix, node in enumerate(flow_serialized["nodes"]):
        node = node["id"]
        if node["_node_id"] == node_id:
            assert node["kls"] == "Subflow"
            nodes_to_add.extend([{"id": subflow_n} for subflow_n in node["subflow_nodes"]])
            edges_to_add.extend(node["subflow_links"])
            break
    else:
        raise ValueError(f"Node with id {node_id} not found in {flow_serialized['nodes']}")

    pos_x = node["pos_x"]
    pos_y = node["pos_y"]

    subflow_data = flow_serialized["nodes"][ix]

    for node in nodes_to_add:
        node["id"]["pos_x"] += pos_x
        node["id"]["pos_y"] += pos_y
        node_ids.append(node["id"]["_node_id"])

    return node_ids, subflow_data, nodes_to_add, edges_to_add, ix


def adapt_flow_data(data):
    data = deepcopy(data)

    # check node compat
    nodes_to_adapt = defaultdict(list)
    subflows_to_regroup = {}

    all_node_to_add, all_edges_to_add, all_ix = [], [], []
    for n in data["nodes"]:
        n = n["id"]
        kls, *_ = factory.MAP[n["kls"]]
        version_from = n.get("PLURALLY_VERSION", 0)

        # first ungroup subflows if necessary:
        if kls is Subflow:
            ungroup = False
            for child in n["subflow_nodes"]:
                kls, *_ = factory.MAP[child["kls"]]
                version_from = child.get("PLURALLY_VERSION", 0)
                if kls.PLURALLY_VERSION != version_from and kls.PLURALLY_VERSION != 0:
                    ungroup = True
            if ungroup:
                logger.debug(f"Ungrouping subflow {n['name']} ({n['_node_id'][:5]}) to adapt versions")
                subnode_ids, subflow_data, nodes_to_add, edges_to_add, ix = ungroup_subflow_data(data, n["_node_id"])
                all_node_to_add.extend(nodes_to_add)
                all_edges_to_add.extend(edges_to_add)
                all_ix.append(ix)

                subflows_to_regroup[n["_node_id"]] = {
                    "nodes_ids": subnode_ids,
                    "subflow_data": subflow_data,
                }

    # delete subflows:
    data["nodes"] = [n for ix, n in enumerate(data["nodes"]) if ix not in all_ix]
    for node in all_node_to_add:
        data["nodes"].append(node)
    data["links"].extend(all_edges_to_add)

    rm_ixs = []
    connected_to_run_handle = []
    for ix, edge in enumerate(data["links"]):
        if edge["target"] in subflows_to_regroup:
            if edge["tgt_handle"] == "run":
                connected_to_run_handle.append(deepcopy(edge))
                rm_ixs.append(ix)

    data["links"] = [edge for ix, edge in enumerate(data["links"]) if ix not in rm_ixs]
    # important to do 2 passes as the pass below modifies in place
    for edge in data["links"]:
        if edge["target"] in subflows_to_regroup:
            if edge["tgt_handle"] == "run":
                # will be reconstructed with connected_to_run_handle
                continue
            else:
                new_target, new_tgt_handle = edge["tgt_handle"].split(".")
                logger.debug(f"Changing from {edge['target'][:5]} target to {new_target[:5]} and tgt_handle to {new_tgt_handle}")
                edge["tgt_handle"] = new_tgt_handle
                edge["target"] = new_target
                edge["key"] = f"{edge['src_handle']}###{new_tgt_handle}"

        if edge["source"] in subflows_to_regroup:
            new_source, new_src_handle = edge["src_handle"].split(".")
            logger.debug(f"Changing from {edge['source'][:5]} source to {new_source[:5]} and src_handle to {new_src_handle}")
            edge["source"] = new_source
            edge["src_handle"] = new_src_handle
            edge["key"] = f"{new_src_handle}###{edge['tgt_handle']}"

    for n in data["nodes"]:
        n = n["id"]
        kls, *_ = factory.MAP[n["kls"]]
        version_from = n.get("PLURALLY_VERSION", 0)
        if kls.PLURALLY_VERSION != version_from and kls.PLURALLY_VERSION != 0:
            nodes_to_adapt[kls].append(n["_node_id"])

    # first of all, let's assert all links are valid
    valid_srcs = {(n["id"]["_node_id"], handle) for n in data["nodes"] for handle in n["id"]["src_handles"]}
    valid_tgts = {(n["id"]["_node_id"], handle) for n in data["nodes"] for handle in n["id"]["tgt_handles"]}
    for link in data["links"]:
        assert (
            link["source"],
            link["src_handle"],
        ) in valid_srcs, f"Invalid source {link}"
        assert (
            link["target"],
            link["tgt_handle"],
        ) in valid_tgts, f"Invalid target {link}"

    for kls, node_ids in nodes_to_adapt.items():
        assert len(set(node_ids)) == len(node_ids), f"Duplicate node ids: {node_ids}"
        kls.adapt_version(node_ids, data)

    # FIXME: should regroup here...
    # for subflow_id, (node_ids, connected_to_run) in ungrouped.items():
    # flow_utils.regroup_subflow_data(data, subflow_id, node_ids, connected_to_run)
    return data, subflows_to_regroup, connected_to_run_handle

import io
import json
import os
import re
import subprocess
import uuid
from collections import defaultdict, deque
from contextlib import suppress
from copy import deepcopy
from pprint import pprint
from typing import Any, Dict, List, Union

import tenacity
from loguru import logger
from pydantic import BaseModel, create_model
from redis import Redis
from rq import Queue, Worker, get_current_job
from rq.registry import FailedJobRegistry

from plurally.json_utils import replace_refs
from plurally.models import factory, flow_utils, utils
from plurally.models.meta import InstagramNewDm, InstagramSendDm
from plurally.models.node import Node
from plurally.models.source.constant import ConstantSource
from plurally.models.subflow import Subflow
from plurally.storage_utils import download_from_s3


def pretty_for_pprint(data, max_bytes_length=10, max_str_length=128):
    return ""
    if isinstance(data, bytes):
        return data[:max_bytes_length]
    if isinstance(data, str):
        return data[:max_str_length]
    elif isinstance(data, dict):
        return {key: pretty_for_pprint(value, max_bytes_length) for key, value in data.items()}
    elif isinstance(data, BaseModel):
        return pretty_for_pprint(data.model_dump(), max_bytes_length)
    elif isinstance(data, list):
        return [pretty_for_pprint(item, max_bytes_length) for item in data]
    elif isinstance(data, tuple):
        return tuple(pretty_for_pprint(item, max_bytes_length) for item in data)
    else:
        return data


def save_debug_info(current_job, sorted_nodes):
    if not current_job:
        return
    all_outputs = {}
    for i, item in enumerate(sorted_nodes):
        if isinstance(item, Node):
            all_outputs[f"{i}_{item.name}"] = item.outputs
    json_str = json.dumps(
        all_outputs,
        indent=4,
        default=lambda x: "" if isinstance(x, bytes) else str(x),
    )
    current_job.meta["debug"] = json.loads(json_str)
    current_job.save_meta()


class FlowResults(BaseModel):
    overrideable_data: List[Dict[str, Any]] = []


class Flow:
    @staticmethod
    def create_id():
        return f"fl-{str(uuid.uuid4())}"

    def __init__(self, name: str = "") -> None:
        global nx
        import networkx as nx

        self._flow_id = Flow.create_id()
        self.name = name
        self.graph = nx.MultiDiGraph()
        self._inter_subflow_run_links = {}
        self.worker = None

    @property
    def flow_id(self):
        return self._flow_id

    def __eq__(self, other: "Flow") -> bool:
        return isinstance(other, Flow) and self.graph.nodes == other.graph.nodes and self.graph.edges == other.graph.edges

    def __contains__(self, node: Node):
        assert isinstance(node, Node)
        return node in self.graph

    def get_scopes_and_meta_data(self):
        scopes_and_meta_data = []
        for child in self.graph.nodes:
            child_scopes_and_meta_datas = child.get_scopes_and_meta_data()
            for child_scopes_and_meta_data in child_scopes_and_meta_datas:
                child_scopes = child_scopes_and_meta_data[0]
                if child_scopes:
                    scopes_and_meta_data.append(child_scopes_and_meta_data)
        return scopes_and_meta_data

    def add_node(
        self,
        node: Node,
        subflow_id: str = None,
    ) -> Node:
        if node in self:
            raise ValueError(f"Block with id={node.node_id[:7]} already registered")
        if subflow_id:
            subflow = self.get_node(subflow_id)
            graph = subflow.graph
        else:
            graph = self.graph
        graph.add_node(node)
        return node

    def get_node(self, node_id: str, traverse_subflows: bool = False) -> Node:
        for child in self.graph.nodes:
            if isinstance(child, (Node, Subflow)) and child.node_id == node_id:
                return child
            if isinstance(child, Subflow) and traverse_subflows:
                with suppress(ValueError):
                    return child.get_node(node_id)
        raise ValueError(f"Node with {node_id=} not found")

    def connect_nodes(
        self,
        src_node: Union[str, "Node"],
        src_handle: str,
        tgt_node: Union[str, "Node"],
        tgt_handle: str,
        subflow: Union[str, "Subflow"] = None,
    ):
        """Connect this node's output to another node's input."""
        if subflow is None:
            flow_or_subflow = self
        else:
            subflow = self.get_node(subflow) if isinstance(subflow, str) else subflow
            flow_or_subflow = subflow

        if isinstance(src_node, str):
            src_node = flow_or_subflow.get_node(src_node)
        else:
            assert src_node in flow_or_subflow.graph, f"{src_node} not in {flow_or_subflow.graph}"

        if isinstance(tgt_node, str):
            tgt_node = flow_or_subflow.get_node(tgt_node)
        else:
            assert tgt_node in flow_or_subflow.graph, f"{tgt_node} not in {flow_or_subflow.graph}"

        # Connection helpers for Instagram nodes
        if (
            isinstance(src_node, InstagramNewDm)
            and isinstance(tgt_node, InstagramSendDm)
            and src_handle == "sender_username"
            and tgt_handle == "recipient_id"
        ):
            return self.connect_nodes(src_node, "sender_id", tgt_node, "recipient_id", subflow)

        return flow_utils.connect_nodes(flow_or_subflow.graph, src_node, src_handle, tgt_node, tgt_handle)

    def disconnect_nodes(
        self,
        src_node: Union[str, "Node"],
        src_handle: str,
        tgt_node: Union[str, "Node"],
        tgt_handle: str,
        subflow: Union[str, "Subflow"] = None,
    ):
        """Disconnect this node connection."""

        if subflow is None:
            flow_or_subflow = self
        else:
            subflow = self.get_node(subflow) if isinstance(subflow, str) else subflow
            flow_or_subflow = subflow

        if isinstance(src_node, str):
            src_node = flow_or_subflow.get_node(src_node)
        if isinstance(tgt_node, str):
            tgt_node = flow_or_subflow.get_node(tgt_node)
        if src_node is tgt_node:
            raise ValueError(f"Cannot connect node with itself: {src_node}")
        try:
            flow_or_subflow.graph.remove_edge(src_node, tgt_node, key=f"{src_handle}###{tgt_handle}")
        except nx.NetworkXError:
            raise ValueError(f"Connection between {src_node} and {tgt_node} with {src_handle=} and {tgt_handle=} not found")

    def delete_node(self, node: Union[str, "Node"], traverse_subflows: bool = False):
        """Remove a node from the flow."""
        node_id = node if isinstance(node, str) else node.node_id
        for child in self.graph.nodes:
            if isinstance(child, Subflow) and traverse_subflows:
                with suppress(ValueError):
                    child.delete_node(node_id)
                    flow_utils.disconnect_all_nodes_connected_to(child.graph, node_id, None, mode="all")
                    # need to disconnect subflow's handles as well
                    edges_to_rm = []
                    for src, tgt, key in self.graph.edges:
                        src_handle, tgt_handle = key.split("###")
                        if (src_handle.startswith(node_id) and src == child) or (tgt_handle.startswith(node_id) and tgt == child):
                            edges_to_rm.append((src, tgt, key))
                    for src, tgt, key in edges_to_rm:
                        self.graph.remove_edge(src, tgt, key=key)
                    return
            if isinstance(child, (Node, Subflow)) and child.node_id == node_id:
                self.graph.remove_node(child)
                return
        raise ValueError(f"Node with id {node_id} not found")

    def run_callbacks(self, items: list[Node]):
        for item in items:
            item.callback()

    @tenacity.retry(
        wait=tenacity.wait_fixed(10),
        stop=tenacity.stop_after_delay(60),
        retry=tenacity.retry_if_exception_type(ValueError),
    )
    def start_worker(self):
        graph = self.get_flatten_graph()
        trigger_node = None
        for child in graph.nodes:
            if isinstance(child, Node) and child.is_trigger:
                trigger_node = child
                break
        if trigger_node:
            if trigger_node.start_worker():
                redis_url = os.environ.get("PLURALLY_REDIS_URL")
                redis_q = os.environ.get("PLURALLY_REDIS_QUEUE")
                worker_name = os.environ.get("PLURALLY_WORKER_NAME")

                assert redis_url, "Redis URL not set"
                assert redis_q, "Redis queue not set"

                if not self.worker:
                    # first check if there is an existing worker
                    for worker in Worker.all(connection=Redis.from_url(redis_url)):
                        if worker.name == worker_name:
                            logger.warning(f"Worker {worker_name} already exists")
                            self.stop_worker(worker)
                            raise ValueError(f"Worker {worker_name} already exists")

                    logger.info(f"Starting worker for {self}")
                    args = [
                        "rq",
                        "worker",
                        "--url",
                        redis_url,
                        redis_q,
                        "--name",
                        worker_name,
                        "-c",
                        "plurally.sentry_settings",
                    ]
                    subprocess.Popen(args)
                    logger.info(f"Worker started for {self}")
                    self.worker = worker_name
                return True

    def stop_worker(self, worker: Worker):
        if worker:
            logger.debug(f"Stopping worker {worker}")
            worker.register_death()

    def __del__(self):
        if self.worker:
            redis_url = os.environ.get("PLURALLY_REDIS_URL")
            if not redis_url:
                raise ValueError("Redis URL not set - cannot stop worker")
            key = f"rq:worker:{self.worker}"
            worker = Worker.find_by_key(key, connection=Redis.from_url(redis_url))
            if not worker:
                logger.warning(f"Worker {self.worker} not found for termination")
                return
            logger.debug(f"Stopping worker {self.worker}")
            self.stop_worker(worker)

    def get_worker_issues(self):
        redis_url = os.environ.get("PLURALLY_REDIS_URL")
        redis_q = os.environ.get("PLURALLY_REDIS_QUEUE")

        assert redis_url is not None, "PLURALLY_REDIS_URL is not set"
        assert redis_q is not None, "PLURALLY_REDIS_QUEUE is not set"

        redis_conn = Redis.from_url(redis_url)
        queue = Queue(redis_q, connection=redis_conn)

        failed_job_registry = FailedJobRegistry(queue=queue)
        failed_job_ids = failed_job_registry.get_job_ids()

        issues = deque(maxlen=10)
        for job_id in failed_job_ids:
            job = queue.fetch_job(job_id)
            if job:
                res = job.latest_result()
                if res and res.type == res.Type.FAILED:
                    match = re.search(r"RuntimeError: (.*)", res.exc_string)
                    if match:
                        exc_val = match.group(1)
                        try:
                            if exc_val not in [i[1] for i in issues]:
                                issues.append((res.created_at, exc_val))
                        except Exception as e:
                            logger.exception(e)
                    else:
                        logger.error("Could not parse error")
                        # logger.debug(f"Full error: {res.exc_string}")

        return issues

    @staticmethod
    def get_sorted_nodes(graph) -> List[Node]:
        return list(nx.topological_sort(graph))

    def get_flatten_graph(self):
        return flow_utils.get_flatten_graph(self.graph)

    def get_flatten_subflow(self, subflow_id) -> tuple["Flow", Subflow]:
        subflow = self.get_node(subflow_id)
        graph = flow_utils.get_flatten_graph(subflow.graph)
        flow = Flow(subflow.name)
        flow.graph = graph
        return flow, subflow

    def resolve_auto_output_types(self, graph):
        for node in graph.nodes:
            node.resolve_output_type(graph)

    def resolve_auto_input_types(self, graph):
        for node in graph.nodes:
            node.resolve_input_type(graph)

    def resolve_types(self, graph):
        for node in graph.nodes:
            node.resolve_output_type_self()
            node.resolve_input_type_self()
        self.resolve_auto_input_types(graph)
        self.resolve_auto_output_types(graph)

    def __call__(self, output_overrides: Dict[str, BaseModel] = None) -> Any:
        state = self.states()
        graph = self.get_flatten_graph()
        overrideable_data = []

        try:
            output_overrides = output_overrides if output_overrides else {}
            if output_overrides:
                logger.debug(f"Will override for nodes: {','.join(output_overrides)}")
            no_run = set()

            def _skip_successors(n):
                for node in graph.successors(n):
                    no_run.add(node)

            sorted_nodes = self.get_sorted_nodes(graph)

            trigger_ix = None
            for node in sorted_nodes:
                if node.is_trigger:
                    trigger_ix = node

                if not isinstance(node, Node):
                    break

                if isinstance(node, ConstantSource):
                    # constant source always have outputs and it is not reset at every iteration
                    continue

                node.outputs = {}

            assert trigger_ix, "Flow must have a trigger block"

            # make sure trigger block is the first one
            # this will make sure that the flow is immediatly aborted if the trigger node has no outputs
            sorted_nodes.remove(trigger_ix)
            sorted_nodes = [trigger_ix] + sorted_nodes

            self.resolve_types(graph)
            current_job = get_current_job()

            if current_job:
                output_schemas = {}
                for node in sorted_nodes:
                    if node.is_output_fixable:
                        named_output_schema = create_model(node.name, __base__=node.OutputSchema)
                        output_schemas[node.node_id] = replace_refs(named_output_schema.model_json_schema())
                current_job.meta["output_schemas"] = output_schemas
                current_job.save_meta()

            for node_ix, node in enumerate(sorted_nodes):
                if current_job:
                    current_job.meta["current_desc"] = node.name
                    current_job.meta["progress"] = int(((node_ix + 1) / len(sorted_nodes)) * 100)
                    current_job.save_meta()

                try:
                    if not isinstance(node, Node):
                        break
                    if node in no_run:
                        _skip_successors(node)
                        continue
                    logger.debug(f"{node} is running")

                    kwargs = {}
                    for src_node, tgt_node, attrs in graph.in_edges(node, True):
                        src_handle = attrs["src_handle"]
                        tgt_handle = attrs["tgt_handle"]

                        assert src_node.outputs is not None, f"{src_node} has no outputs"

                        src_value = src_node.outputs.get(src_handle)
                        # if tgt is list and src is not, append
                        if utils.is_list_type(tgt_node.InputSchema.model_fields[tgt_handle]) and not utils.is_list_type(
                            src_node.OutputSchema.model_fields[src_handle]
                        ):
                            if tgt_handle not in kwargs:
                                kwargs[tgt_handle] = []
                            kwargs[tgt_handle].append(src_value)
                            os.environ.get("VERBOSE") and print(f"Adding list input for {tgt_handle=}: {pretty_for_pprint(src_value)}")
                        else:
                            kwargs[tgt_handle] = src_value
                            os.environ.get("VERBOSE") and print(f"Adding non list input for {tgt_handle=}: {pretty_for_pprint(src_value)}")

                    node_overrides = output_overrides.get(node.node_id)
                    if node_overrides:
                        logger.debug(f"Overriding execution of {node}")
                        if isinstance(node_overrides, dict):
                            node_overrides = node.OutputSchema(**node_overrides)
                        node.outputs = node_overrides.model_dump()
                    else:
                        is_no_run = not kwargs.get("run", True)
                        if is_no_run:
                            logger.debug(f"Skipping {node} - run is set to False")
                            _skip_successors(node)
                            continue

                        logger.debug(f"Forwarding {node} with {list(kwargs)}")

                        if os.environ.get("VERBOSE"):
                            print("#### INPUTS ####")
                            pprint(pretty_for_pprint(kwargs))

                        node(**kwargs)

                        if node.outputs is None:
                            logger.debug(f"Node {node} has no outputs - successors will not run")
                            _skip_successors(node)
                        else:
                            if os.environ.get("VERBOSE"):
                                print("#### OUTPUTS ####")
                                pprint(pretty_for_pprint(node.outputs))

                        save_debug_info(current_job, sorted_nodes)

                        node.early_stop_if_needed(graph)

                        if node.is_trigger and node.outputs is None:
                            # skip if trigger has no outputs
                            logger.debug(f"Aborting execution due to missing outputs from {node}")
                            self.run_callbacks(sorted_nodes)
                            return

                    od = node.get_overrideable_data()
                    if od:
                        overrideable_data.append({"node_id": node.node_id, "data": od})

                except Exception as e:
                    # if RetryError is raised, log the source
                    if isinstance(e, tenacity.RetryError):
                        e = e.last_attempt.exception()
                    raise RuntimeError(f"{type(node).__name__} failed: {e}").with_traceback(e.__traceback__)

            self.run_callbacks(sorted_nodes)

            results = FlowResults(overrideable_data=overrideable_data)

            if current_job:
                overrideable_data = results.model_dump(mode="json")["overrideable_data"]
                current_job.meta["overrideable_data"] = overrideable_data
                current_job.save_meta()

            return results
        except Exception:
            self.update(state)
            raise

    def __str__(self) -> str:
        return f"{type(self).__name__}(name={self.name}, id={self._flow_id[:4]})"

    def create_subflow(self, name: str, node_ids: list[str]) -> "Flow":
        assert len(node_ids) > 1, "Subflow must have at least two nodes"
        subflow_node_ids = set()
        subflow_nodes = []
        for node_id in node_ids:
            node = self.get_node(node_id)
            assert not isinstance(node, Subflow), "Cannot nest subflows"
            subflow_node_ids.add(node_id)
            subflow_nodes.append(node)

        # subflow_links are the inner links of the subflow
        subflow_links = set()
        # inter_flow_links are the links between the subflow and the rest of the flow
        inter_flow_links = set()
        inter_subflow_run_links = []
        force_show_src = []
        for node in subflow_nodes:
            in_edges = list(self.graph.in_edges(node, data=True))
            for src, _, key in in_edges:
                assert _ is node

                if src.node_id in subflow_node_ids:
                    subflow_links.add(
                        (
                            src.node_id,
                            key["src_handle"],
                            node.node_id,
                            key["tgt_handle"],
                        )
                    )
                else:
                    if key["tgt_handle"] == "run":
                        # connect to subflow's run, not inner node's run
                        # and save the connection to be reconnected later
                        subflow_tgt_handle = "run"
                        inter_subflow_run_links.append((src.node_id, key["src_handle"], node.node_id, "run"))
                    else:
                        subflow_tgt_handle = f"{node.node_id}.{key['tgt_handle']}"
                    inter_flow_links.add((src.node_id, key["src_handle"], None, subflow_tgt_handle))

            out_edges = list(self.graph.out_edges(node, data=True))
            for _, tgt, key in out_edges:
                assert _ is node
                if tgt.node_id in subflow_node_ids:
                    subflow_links.add(
                        (
                            node.node_id,
                            key["src_handle"],
                            tgt.node_id,
                            key["tgt_handle"],
                        )
                    )
                else:
                    src_handle = f"{node.node_id}.{key['src_handle']}"
                    force_show_src.append(src_handle)
                    inter_flow_links.add((None, src_handle, tgt.node_id, key["tgt_handle"]))

        min_x = min([node.pos_x for node in subflow_nodes])
        max_x = max([node.pos_x for node in subflow_nodes])
        pos_x = (min_x + max_x) // 2

        min_y = min([node.pos_y for node in subflow_nodes])
        max_y = max([node.pos_y for node in subflow_nodes])
        pos_y = (min_y + max_y) // 2

        # make them relative to the top left
        for node in subflow_nodes:
            node.pos_x -= pos_x
            node.pos_y -= pos_y

        subflow = Subflow(
            Subflow.InitSchema(
                name=name,
                pos_x=pos_x,
                pos_y=pos_y,
            ),
            nodes=subflow_nodes,
            links=subflow_links,
            force_show_src=force_show_src,
        )

        # this is to reconstruct the inter flow links to inner nodes' run handles
        # observe that they might have been changed by the time we ungroup the subflow
        # and in this case we will not be able to reconnect them (which is fine)
        self._inter_subflow_run_links[subflow.node_id] = inter_subflow_run_links

        for node in subflow_nodes:
            self.delete_node(node)

        self.add_node(subflow)
        for src, src_handle, tgt, tgt_handle in inter_flow_links:
            self.connect_nodes(src or subflow, src_handle, tgt or subflow, tgt_handle)

        if not nx.is_directed_acyclic_graph(self.graph):
            raise ValueError("Resulting subflow is not valid")

        return subflow

    def ungroup_subflow(self, subflow: Subflow | str):
        if isinstance(subflow, str):
            subflow = self.get_node(subflow)
        assert subflow in self.graph, f"Subflow {subflow} not found in the current Flow"
        subflow_nodes = list(subflow.graph.nodes)
        inner_subflow_links = list(subflow.graph.edges(data=True))

        for node in subflow_nodes:
            node.pos_x += subflow.pos_x
            node.pos_y += subflow.pos_y
            self.add_node(node)

        for src, tgt, key in inner_subflow_links:
            src_handle = key["src_handle"]
            tgt_handle = key["tgt_handle"]
            self.connect_nodes(src, src_handle, tgt, tgt_handle)

        inter_flow_edges = set()
        inter_flow_in_edges = self.graph.in_edges(subflow, data=True)
        for src, _, data in inter_flow_in_edges:
            src_handle = data["src_handle"]
            if data["tgt_handle"] == "run":
                # these inter_flow links are saved in _inter_subflow_run_links
                continue

            tgt_node_id, tgt_handle = data["tgt_handle"].split(".")
            inter_flow_edges.add((src, src_handle, subflow.get_node(tgt_node_id), tgt_handle))

        inter_flow_out_edges = self.graph.out_edges(subflow, data=True)
        for _, tgt, data in inter_flow_out_edges:
            src_node_id, src_handle = data["src_handle"].split(".")
            tgt_handle = data["tgt_handle"]
            inter_flow_edges.add((subflow.get_node(src_node_id), src_handle, tgt, tgt_handle))

        inter_subflow_run_links = self._inter_subflow_run_links.pop(subflow.node_id, [])
        self.delete_node(subflow)

        # here subflow must be disconnected otherwise
        # we might end up with multiple connections
        for inter_flow_edge in inter_flow_edges:
            self.connect_nodes(*inter_flow_edge)

        for src, src_handle, tgt, tgt_handle in inter_subflow_run_links:
            # nodes could have been deleted or handles changed by now
            with suppress(Exception):
                self.connect_nodes(src, src_handle, tgt, tgt_handle)

    def _get_title(self, schema, handle):
        return schema.model_fields[handle].title or handle.title().replace("_", " ")

    def serialize(self) -> Dict:
        input_schemas = utils.get_input_schemas(self.graph.nodes, to_json=False)
        output_schemas = utils.get_output_schemas(self.graph.nodes, to_json=False)

        s = nx.node_link_data(self.graph)
        s["nodes"] = [{**n, "id": n["id"].serialize()} for n in s["nodes"]]

        links = []
        for link in s["links"]:
            try:
                source = link["source"]
                target = link["target"]

                src_handle_title = self._get_title(output_schemas[source.node_id], link["src_handle"])
                tgt_handle_title = self._get_title(input_schemas[target.node_id], link["tgt_handle"])

                label = f"{src_handle_title} -> {tgt_handle_title}"
                links.append(
                    {
                        **link,
                        "label": label,
                        "source": source.node_id,
                        "target": target.node_id,
                    }
                )
            except Exception:
                logger.warning("could not add link")

        s["links"] = links
        s["name"] = self.name
        s["id"] = self.flow_id
        s["_inter_subflow_run_links"] = self._inter_subflow_run_links
        return s

    def states(self) -> Dict[str, Dict]:
        all_states = {}
        for child in self.graph.nodes:
            all_states[child.node_id] = child.state()
        return all_states

    def update(self, state: Dict[str, Dict]):
        for child in self.graph.nodes:
            state_update = state.get(child.node_id)
            child.update_state(state_update)

    @classmethod
    def parse(cls, data: Dict) -> "Flow":
        global nx
        import networkx as nx

        data = deepcopy(data)

        flow = cls()
        nodes = {}
        nodes_list = []
        for n in data["nodes"]:
            node = factory.create_node(**n["id"])
            nodes[node.node_id] = node
            nodes_list.append(node)
        data["nodes"] = [{**n, "id": nodes[n["id"]["_node_id"]]} for n in data["nodes"]]
        data["links"] = [{**link, "source": nodes[link["source"]], "target": nodes[link["target"]]} for link in data["links"]]

        flow.graph = nx.node_link_graph(data)
        flow._flow_id = data.get("id", "no-id")
        flow.name = data.get("name", "no-name")
        flow._inter_subflow_run_links = data.get("_inter_subflow_run_links", {})
        return flow

    def get_necessary_env_vars(self) -> List[str]:
        env_vars = []
        for node in self.graph.nodes:
            env_vars.extend(node.get_necessary_env_vars())
        return env_vars

    @classmethod
    def num_triggers(cls, graph):
        n = 0
        for child in graph.nodes:
            if isinstance(child, Node) and child.is_trigger:
                n += 1
        return n

    def _get_insta_issues(self, graph, insta_nodes):
        issues = []
        send_dm_nodes = [node for node in insta_nodes if isinstance(node, InstagramSendDm)]
        if len(send_dm_nodes) > 1:
            issues.append("Flow can only have one 'Send DM (Insta)' block")

        new_dm_nodes = [node for node in insta_nodes if isinstance(node, InstagramNewDm)]
        if send_dm_nodes:
            [send_dm_node] = send_dm_nodes
            if len(new_dm_nodes) != 1:
                issues.append("In order to send Instagram DMs, you need to use exactly one the 'Incoming DM (Insta)' block.")
            else:
                [new_dm_node] = new_dm_nodes
                # elif not connected to the 'Incoming DM (Insta)' block:
                if not any(
                    [
                        (src, tgt, key)
                        for src, tgt, key in graph.in_edges(send_dm_node, data=True)
                        if all(
                            [
                                key["tgt_handle"] == "recipient_id",
                                key["src_handle"] == "sender_id",
                                src == new_dm_node,
                                tgt == send_dm_node,
                            ]
                        )
                    ]
                ):
                    issues.append(
                        "The 'Incoming DM (Insta)' sender ID output must be connected to the 'Send DM (Insta)' recipient ID input."
                    )

                # elif not connected to the 'Incoming DM (Insta)' block:
                if not any(
                    [
                        (src, tgt, key)
                        for src, tgt, key in graph.in_edges(send_dm_node, data=True)
                        if all(
                            [
                                key["tgt_handle"] == "was_escalated_previously_",
                                key["src_handle"] == "was_escalated_previously_",
                                src == new_dm_node,
                                tgt == send_dm_node,
                            ]
                        )
                    ]
                ):
                    issues.append(
                        "The 'Incoming DM (Insta)' Is Escalation Triggered output must be connected to the 'Send DM (Insta)' run input."
                    )
        return issues

    def get_issues(self) -> List[str]:
        issues = []
        try:
            graph = self.get_flatten_graph()
        except ValueError as e:
            # could fail if incompatible types after type change...
            logger.exception(e)
            return [e.args[0]]

        if not nx.is_directed_acyclic_graph(graph):
            issues.append("Graph is not a directed acyclic graph")

        num_triggers = self.num_triggers(graph)
        if num_triggers == 0:
            issues.append("Flow is missing a trigger block")

        if num_triggers > 1:
            issues.append("Flow can only have one trigger block")

        if not graph.nodes:
            issues.append("Flow is empty")

        # ensure that all nodes are connected (when handle is not optional)
        insta_nodes = set()
        for node in graph.nodes:
            if isinstance(node, (InstagramSendDm, InstagramNewDm)):
                insta_nodes.add(node)
            required_inputs = utils.get_required_fields(node.InputSchema)
            for input_name in required_inputs:
                if not any([(src, tgt, key) for src, tgt, key in graph.in_edges(node, data=True) if key["tgt_handle"] == input_name]):
                    issues.append(f"Node {node.name} is missing required input {input_name}")

            if node.EnvVars:
                logger.debug(f"Loading env vars for {node}")
                issues.extend(node.EnvVars.get_issues())

            # this will duplicate issue with node.EnvVars above - minor
            for env_var_key in node.get_necessary_env_vars():
                if env_var_key not in os.environ:
                    issues.append(f"{node.name} requires environment variable {env_var_key}")
        issues.extend(self._get_insta_issues(graph, insta_nodes))

        for node in graph.nodes:
            issues.extend(node.get_issues(graph))
        return issues

    def is_valid(self) -> bool:
        return not self.get_issues()

    def get_source_nodes(self) -> List[Node]:
        if not self.is_valid():
            raise ValueError("Cannot get source nodes on invalid flow")
        source_nodes = []
        graph = self.get_flatten_graph()
        for child in graph:
            if isinstance(child, Node) and graph.in_degree(child) == 0:
                source_nodes.append(child)
        return source_nodes

    def _delete_sensitive_fields(self, node):
        kls, *_ = factory.MAP[node["kls"]]
        if kls == Subflow:
            for child in node["subflow_nodes"]:
                self._delete_sensitive_fields(child)
        else:
            for sensitive_field in kls.SensitiveFields:
                if sensitive_field in node:
                    del node[sensitive_field]

    def create_template(self):
        template = self.serialize()
        for node in template["nodes"]:
            self._delete_sensitive_fields(node["id"])
        return template

    @classmethod
    def _get_overrides_for_node(cls, node_attrs):
        name = node_attrs["name"]
        kls, *_ = factory.MAP[node_attrs["kls"]]
        overrides = {}
        if kls == Subflow:
            for child in node_attrs["subflow_nodes"]:
                overrides.update(cls._get_overrides_for_node(child))
        else:
            init_schema = kls.InitSchema.model_fields
            overrideable_fields = kls.InitSchema.get_overrideable_fields()
            overrides_for_node = {}
            for field_name, field_info in init_schema.items():
                if field_name not in overrideable_fields and (not field_info.is_required() or field_name in node_attrs):
                    continue
                overrides_for_node[field_name] = (field_info.annotation, field_info)
            override_schema = create_model(name, __config__=kls.InitSchema.model_config, **overrides_for_node)
            overrides[node_attrs["_node_id"]] = override_schema
        return overrides

    @classmethod
    def get_overrides_for_template(cls, template) -> Dict[str, BaseModel]:
        required_overrides = {}
        for node in template["nodes"]:
            node_attrs = node["id"]
            required_overrides.update(cls._get_overrides_for_node(node_attrs))
        return required_overrides

    @classmethod
    def from_template(cls, template, data: dict = None):
        data = defaultdict(dict, data or {})

        template = deepcopy(template)
        for node in template["nodes"]:
            node_attrs = node["id"]
            node_id = node["id"]["_node_id"]
            kls, *_ = factory.MAP[node_attrs["kls"]]
            if kls == Subflow:
                for child in node_attrs["subflow_nodes"]:
                    child_data = data[child["_node_id"]]
                    child.update(child_data)
            else:
                node["id"].update(data[node_id])
        return cls.parse(template)

    def disconnect_all_nodes_connected_to(self, node_id: str, handle: str = None, mode: str = "all"):
        return flow_utils.disconnect_all_nodes_connected_to(self.graph, node_id, handle, mode)

    def propagate_new_handle_to_subflows(self, child_node: Node, handle: str, mode: str):
        assert mode in ("source", "target")
        for node in self.graph.nodes:
            if isinstance(node, Subflow) and child_node in node.graph.nodes:
                if mode == "target":
                    node.tgt_handles = list(set(node.tgt_handles) | {f"{child_node.node_id}.{handle}"})
                else:
                    node.src_handles = list(set(node.src_handles) | {f"{child_node.node_id}.{handle}"})

    def add_target_handle(self, node_id: str, src_handle: str) -> str:
        node = self.get_node(node_id)
        return node.add_target_handle(src_handle)

    def add_source_handle(self, node_id: str, tgt_handle: str) -> str:
        node = self.get_node(node_id)
        return node.add_source_handle(tgt_handle)

    def rename_handles(self, node: Node, renamed_handles: Dict[str, str], mode: str):
        connections = []
        deconnections = []
        subflows = [n for n in self.graph.nodes if isinstance(n, Subflow)]
        if mode == "source":
            if node in self.graph:
                for _, tgt, data in self.graph.out_edges(node, data=True):
                    src_handle = data["src_handle"]
                    new_handle = renamed_handles.get(src_handle)
                    if new_handle:
                        deconnections.append((node, src_handle, tgt, data["tgt_handle"]))
                        connections.append((node, new_handle, tgt, data["tgt_handle"]))
            else:
                # node is part of subflow
                for subflow in subflows:
                    if node in subflow.graph:
                        # inner subflow connections
                        for _, tgt, data in subflow.graph.out_edges(node, data=True):
                            src_handle = data["src_handle"]
                            new_handle = renamed_handles.get(src_handle)
                            if new_handle:
                                deconnections.append((node, src_handle, tgt, data["tgt_handle"], subflow))
                                connections.append((node, new_handle, tgt, data["tgt_handle"], subflow))

                        # intra subflow connections
                        for src, tgt, data in self.graph.out_edges(subflow, data=True):
                            src_handle = data["src_handle"]
                            is_subflow_handle = len(src_handle.split(".")) > 1
                            if is_subflow_handle:
                                subflow_node_id, subflow_handle = src_handle.split(".")
                                if subflow_node_id == node.node_id:
                                    new_handle = renamed_handles.get(subflow_handle)
                                    if new_handle:
                                        new_handle = f"{node.node_id}.{new_handle}"
                                        deconnections.append((src, src_handle, tgt, data["tgt_handle"]))
                                        connections.append((src, new_handle, tgt, data["tgt_handle"]))

        elif mode == "target":
            if node in self.graph:
                for src, _, data in self.graph.in_edges(node, data=True):
                    tgt_handle = data["tgt_handle"]
                    new_handle = renamed_handles.get(tgt_handle)
                    if new_handle:
                        deconnections.append((src, data["src_handle"], node, tgt_handle))
                        connections.append((src, data["src_handle"], node, new_handle))
            else:
                # node is part of subflow
                for subflow in subflows:
                    if node in subflow.graph:
                        # inner subflow connections
                        for src, _, data in subflow.graph.in_edges(node, data=True):
                            tgt_handle = data["tgt_handle"]
                            new_handle = renamed_handles.get(tgt_handle)
                            if new_handle:
                                deconnections.append((src, data["src_handle"], node, tgt_handle, subflow))
                                connections.append((src, data["src_handle"], node, new_handle, subflow))

                        # intra subflow connections
                        for src, tgt, data in self.graph.in_edges(subflow, data=True):
                            tgt_handle = data["tgt_handle"]
                            is_subflow_handle = len(tgt_handle.split(".")) > 1
                            if is_subflow_handle:
                                subflow_node_id, subflow_handle = tgt_handle.split(".")
                                if subflow_node_id == node.node_id:
                                    new_handle = renamed_handles.get(subflow_handle)
                                    if new_handle:
                                        new_handle = f"{node.node_id}.{new_handle}"
                                        deconnections.append((src, data["src_handle"], tgt, tgt_handle))
                                        connections.append((src, data["src_handle"], tgt, new_handle))

        for deconnection in deconnections:
            self.disconnect_nodes(*deconnection)
        # need to refresh schemas for subflows here, but not before, otherwise it won't manage
        # to do the disconnections
        for subflow in subflows:
            subflow._set_schemas()

        for connection in connections:
            self.connect_nodes(*connection)

    def refresh_connections(self, node, before_model_fields, after_model_fields, mode: str):
        assert mode in ("source", "target")

        before_handle_ids = {
            (handle_field.json_schema_extra or {}).get("handle_id", handle_name): handle_name
            for handle_name, handle_field in before_model_fields.items()
        }
        after_handle_ids = {
            (handle_field.json_schema_extra or {}).get("handle_id", handle_name): handle_name
            for handle_name, handle_field in after_model_fields.items()
        }

        removed_handles, added_handles = [], []
        renamed_handles = {}
        for handle_id, handle_name in before_handle_ids.items():
            after_handle_name = after_handle_ids.get(handle_id)
            if after_handle_name is None:
                removed_handles.append(handle_name)
            elif handle_name != after_handle_name:
                renamed_handles[handle_name] = after_handle_name
                added_handles.append(after_handle_name)  # need to propagate

        for handle_id, handle_name in after_model_fields.items():
            if handle_id not in before_handle_ids:
                added_handles.append(handle_id)

        for removed_handle in removed_handles:
            self.disconnect_all_nodes_connected_to(node.node_id, removed_handle, mode)
        if renamed_handles:
            self.rename_handles(node, renamed_handles, mode)
        for added_handle in added_handles:
            self.propagate_new_handle_to_subflows(node, added_handle, mode)


def exec_flow(flow_json, exec_data):
    flow = Flow.parse(flow_json)

    # get trigger node
    [trigger_node] = [node for node in flow.get_flatten_graph() if node.is_trigger]
    for val in exec_data[trigger_node.node_id].values():
        if isinstance(val, dict) and "file" in val:
            # modify in place
            logger.debug("Downloading file")
            f = io.BytesIO()
            download_from_s3(val["file"], f)
            val["content"] = f.read()
    flow(exec_data)

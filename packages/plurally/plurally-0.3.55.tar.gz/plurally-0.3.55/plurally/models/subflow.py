from typing import List

import networkx as nx
from loguru import logger
from pydantic import Field, create_model

from plurally.json_utils import replace_refs
from plurally.models import utils
from plurally.models.node import Node

INTEGRATION_ICONS = {"gmail", "email", "openai", "gsheets", "instagram"}


class Subflow(Node):
    ICON = "subflow"

    class InitSchema(Node.InitSchema):
        __doc__ = "Groups multiple blocks into one."
        desc: str = Field(
            "",
            title="Description",
            description="A description of the subflow.",
            examples=["This subflow does X."],
        )

    DESC = InitSchema.__doc__

    def _fill_handles_if_needed(
        self,
        init_inputs,
        nodes,
        src_connected: set,
        tgt_connected: set,
        force_show_src: List[str],
    ):
        # by default we take all nodes that are not connected in the subflow
        if init_inputs.src_handles is None:
            init_inputs.src_handles = []
            for node in nodes:
                for handle in node.src_handles:
                    key = f"{node.node_id}.{handle}"
                    if key not in src_connected:
                        init_inputs.src_handles.append(key)

        if force_show_src:
            # in the case where a handle has an inter flow connection
            # we always want to show it by default
            # users can then hide it if they want
            for handle in force_show_src:
                if handle not in init_inputs.src_handles:
                    init_inputs.src_handles.append(handle)

        if init_inputs.tgt_handles is None:
            init_inputs.tgt_handles = [] if self.is_trigger else ["run"]
            for node in nodes:
                for handle in node.tgt_handles:
                    key = f"{node.node_id}.{handle}"
                    if key not in tgt_connected:
                        init_inputs.tgt_handles.append(key)

    def __init__(
        self,
        init_inputs: Node.InitSchema,
        nodes,
        links,
        force_show_src: List[str] = None,
    ):
        self.graph = nx.MultiDiGraph()
        self.desc = init_inputs.desc
        node_id_to_node = {}
        for node in nodes:
            node_id_to_node[node.node_id] = node
            self.graph.add_node(node)

        src_connected = set()
        tgt_connected = set()
        for src_node, src_handle, tgt_node, tgt_handle in links:
            assert isinstance(src_node, str), src_node
            assert isinstance(tgt_node, str), tgt_node
            try:
                flow_utils.connect_nodes(
                    self.graph,
                    node_id_to_node[src_node],
                    src_handle,
                    node_id_to_node[tgt_node],
                    tgt_handle,
                )
            except Exception:
                logger.warning("Error connecting nodes")
                continue

            src_connected.add(f"{src_node}.{src_handle}")
            tgt_connected.add(f"{tgt_node}.{tgt_handle}")

        self._fill_handles_if_needed(init_inputs, nodes, src_connected, tgt_connected, force_show_src)

        super().__init__(init_inputs)

    @property
    def adapters(self):
        out = {}
        for node in self.graph.nodes:
            for src_handle, adapter in node.adapters.items():
                out[f"{node.node_id}.{src_handle}"] = adapter
        return out

    @Node.pos_x.setter
    def pos_x(self, value):
        offset = value - self._pos_x
        for node in self.graph.nodes:
            node.pos_x += offset
        self._pos_x = value

    @Node.pos_y.setter
    def pos_y(self, value):
        offset = value - self._pos_y
        for node in self.graph.nodes:
            node.pos_y += offset
        self._pos_y = value

    def get_node(self, node_id):
        for child in self.graph.nodes:
            if isinstance(child, Node) and child.node_id == node_id:
                return child
        raise ValueError(f"Node with id {node_id} not found")

    def delete_node(self, node_id):
        node = self.get_node(node_id)
        self.graph.remove_node(node)
        return node

    def _get_fields(self, ignore, fields_type="input"):
        fields = {}
        is_input = fields_type == "input"
        for node in self.graph.nodes:
            schema = node.InputSchema if is_input else node.OutputSchema
            for handle in schema.model_fields:
                if is_input and handle == "run" or (node.node_id, handle) in ignore:
                    continue
                # Extract field annotation and default value from FieldInfo
                field_info = schema.model_fields[handle]
                field_type = field_info.annotation  # Extracting type
                default_value = field_info.default if field_info.default is not Ellipsis else ...
                field_title = f"[{node.name}: {handle}]"
                fields[f"{node.node_id}.{handle}"] = (
                    field_type,
                    Field(default_value, title=field_title),
                )

        return fields

    def _set_schemas(self) -> None:
        # intra_connected_handles should not be showed here
        s = nx.node_link_data(self.graph)
        ignore_src = set()
        ignore_tgt = set()
        for link in s["links"]:
            # any src handle (output) even if connected inside the subflow
            # could potentially be used for inter flow connection
            # should be "hidden" by default though
            ignore_tgt.add((link["target"].node_id, link["tgt_handle"]))

        output_fields = self._get_fields(ignore_src, "output")
        self.OutputSchema = create_model(
            "OutputSchema",
            **output_fields,
            __base__=Node.OutputSchema,
        )

        input_fields = self._get_fields(ignore_tgt, "input")
        self.InputSchema = create_model(
            "InputSchema",
            **input_fields,
            __base__=Node.InputSchema,
        )

    def state(self):
        return {node.node_id: node.state() for node in self.graph.nodes}

    def update_state(self, state_update):
        for node in self.graph.nodes:
            node.update_state(state_update.get(node.node_id))

    def serialize(self):
        s = nx.node_link_data(self.graph)

        input_schemas = utils.get_input_schemas(self.graph.nodes)
        output_schemas = utils.get_output_schemas(self.graph.nodes)

        links = []
        for link in s["links"]:
            links.append(utils.serialize_link(link, input_schemas, output_schemas))

        return super().serialize() | {
            "desc": self.desc,
            "subflow_nodes": [node.serialize() for node in self.graph.nodes],
            "subflow_links": links,
            "output_schema": replace_refs(self.OutputSchema.model_json_schema()),
            "input_schema": replace_refs(self.InputSchema.model_json_schema()),
            "icons": list(set(node.ICON for node in self.graph.nodes if node.ICON in INTEGRATION_ICONS)),
        }

    @classmethod
    def _parse(cls, **kwargs):
        nodes = []
        for node in kwargs.pop("subflow_nodes", []):
            nodes.append(factory.create_node(**node))
        links = []
        for link in kwargs.pop("subflow_links", []):
            links.append(
                (
                    link["source"],
                    link["src_handle"],
                    link["target"],
                    link["tgt_handle"],
                )
            )
        return cls(
            cls.InitSchema(**kwargs),
            nodes,
            links,
        )

    @property
    def is_trigger(self):
        return any(node.is_trigger for node in self.graph.nodes)

    def get_scopes_and_meta_data(self):
        scopes_and_meta_data = []
        for node in self.graph.nodes:
            scopes_and_meta_data.extend(node.get_scopes_and_meta_data())
        return scopes_and_meta_data

    def get_necessary_env_vars(self):
        env_vars = []
        for node in self.graph.nodes:
            env_vars.extend(node.get_necessary_env_vars())
        return env_vars


# meh
from plurally.models import factory, flow_utils  # noqa: E402

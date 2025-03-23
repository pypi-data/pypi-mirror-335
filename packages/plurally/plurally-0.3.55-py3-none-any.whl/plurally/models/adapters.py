from plurally.models.action import format
from plurally.models.misc import Table
from plurally.models.node import get_inner_type


def table_to_str_adapter(src_node, tgt_node, src_handle):
    nodes = [
        format.TableToTextSimple(
            format.TableToTextSimple.InitSchema(
                name="AutoFormat",
                pos_x=(src_node.pos_x + tgt_node.pos_x) / 2,
                pos_y=(src_node.pos_y + tgt_node.pos_y) / 2,
            )
        )
    ]
    table_field = get_inner_type(src_node.OutputSchema.model_fields[src_handle])
    assert table_field.annotation is Table
    connections = [(0, src_handle, 1, "table"), (1, "text", 2, None)]
    return nodes, connections

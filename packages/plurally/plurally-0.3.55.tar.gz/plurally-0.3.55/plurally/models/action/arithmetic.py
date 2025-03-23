import operator

from plurally.models.node import Node


class PrintNode(Node):
    def __init__(self, name):
        super().__init__(name)
        self.inputs["value"] = None


class BinaryOpNode(Node):
    _OP = None

    class InputSchema(Node.InputSchema):
        left: float | int
        right: float | int

    class OutputSchema(Node.OutputSchema):
        result: float

    def forward(self, node_input: InputSchema):
        self.outputs["result"] = self._OP(node_input.left, node_input.right)


class Multiply(BinaryOpNode):
    ICON = "multiply"
    _OP = operator.mul


class Add(BinaryOpNode):
    ICON = "add"
    _OP = operator.add


class Subtract(BinaryOpNode):
    ICON = "subtract"
    _OP = operator.sub


class Divide(BinaryOpNode):
    ICON = "divide"
    _OP = operator.truediv


class Mod(BinaryOpNode):
    _OP = operator.mod


__all__ = [
    "Add",
    "Multiply",
    "Mod",
    "Divide",
    "Subtract",
]

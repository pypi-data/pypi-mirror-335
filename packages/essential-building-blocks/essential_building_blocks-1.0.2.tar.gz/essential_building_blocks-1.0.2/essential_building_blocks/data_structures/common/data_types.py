from typing import Any


class NodeBase:
    """
    A base class for nodes in linked lists, trees, graphs, and other data structures.
    """

    def __init__(self, value: Any):
        self.value = value


class SingleLinkNode(NodeBase):
    """
    A single linked list node.
    """

    def __init__(self, value: Any, next_node: "SingleLinkNode | None" = None):
        super().__init__(value)
        self.next: "SingleLinkNode | None" = next_node

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)


class DoubleLinkNode(NodeBase):
    """
    A double linked list node.
    """

    def __init__(
        self,
        value: Any,
        next_node: "DoubleLinkNode | None" = None,
        prev_node: "DoubleLinkNode | None" = None,
    ):
        super().__init__(value)
        self.next: "DoubleLinkNode | None" = next_node
        self.prev: "DoubleLinkNode | None" = prev_node

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self)

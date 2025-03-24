from typing import List, Any
from anytree import NodeMixin


def get_all_names(nodes: List[NodeMixin]) -> List[str]:
    names = []
    for node in nodes:
        names.append(node.name)
    return names


def find_by_name(nodes: List[NodeMixin], name: Any) -> NodeMixin | None:
    for node in nodes:
        if node.name == name:
            return node

from anytree import PreOrderIter, NodeMixin
from typing import List, Dict, Union, overload, TypeVar

NodeType = TypeVar("NodeType", bound=NodeMixin)


@overload
def group_by_depth(nodes: List[NodeType]) -> Dict[int, List[NodeType]]: ...


@overload
def group_by_depth(root: NodeType) -> Dict[int, List[NodeType]]: ...


def group_by_depth(
    root_or_nodes: Union[List[NodeType], NodeType]
) -> Dict[int, List[NodeType]]:
    grouped_nodes: Dict[int, List[NodeType]] = {}

    if isinstance(root_or_nodes, list):
        nodes = root_or_nodes
    else:
        nodes = PreOrderIter(root_or_nodes)

    for node in nodes:
        if node.depth not in grouped_nodes:
            grouped_nodes[node.depth] = [node]
        else:
            grouped_nodes[node.depth].append(node)

    return grouped_nodes

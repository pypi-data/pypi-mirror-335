from anytree import Node, findall
from crimson.anytree_extension.utils.arranger import group_by_depth
from typing import Callable, List, Any
from crimson.anytree_extension.types.fn import FilterFn


def get_all_unique_names(nodes: List[Node], unique_key: str) -> List[str]:
    names = []
    for node in nodes:
        names.append(getattr(node, unique_key))
    return names


def find_by_value(nodes: List[Node], value: Any, value_key: str) -> Node | None:
    for node in nodes:
        if getattr(node, value_key) == value:
            return node


def collapse(
    tree: Node,
    unique_key: str,
    filter: FilterFn[Callable[[Node], bool]],
    safeguard: bool = True,
):
    new_nodes: List[Node] = []
    nodes_to_take: List[Node] = list(findall(tree, filter))
    if tree not in nodes_to_take:
        nodes_to_take.append(tree)

    all_names = get_all_unique_names(nodes_to_take, unique_key)
    if len(all_names) != len(set(all_names)):
        if safeguard is True:
            raise Exception(
                """
This function is implemented assuming all of your nodes have a unique name.
If you still want to run this function, set `safeguard` False.
"""
            )
        else:
            pass

    grouped_nodes = group_by_depth(nodes_to_take)
    depths = sorted(grouped_nodes.keys())

    for depth in depths:
        for node in grouped_nodes[depth]:
            kwargs = {
                key: value
                for key, value in node.__dict__.items()
                if not key.startswith("_")
            }
            if depth == 0:
                new_root = Node(**kwargs)
                new_nodes.append(new_root)
            else:
                for old_parent in reversed(node.path):
                    parent_candidate = find_by_value(new_nodes, old_parent.name, "name")
                    if parent_candidate is not None:
                        new_nodes.append(Node(**kwargs, parent=parent_candidate))
                        break
                if parent_candidate is None:
                    raise Exception(
                        f"{node.name} should have at least one valid parent candidate. There is something wrong."
                    )
    return new_root

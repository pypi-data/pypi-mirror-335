from anytree import NodeMixin
from typing import Generic, Tuple
from crimson.anytree_extension.types.node import NodeType
from crimson.anytree_extension.utils.arranger import group_by_depth
from anytree.node.util import _repr


def add_index_to_duplicated_children_name_init(parent: NodeType):
    name_counts = {}
    for child in parent.children:
        child: UniqueNode = child
        child_name_str = str(child.name)
        if child_name_str in name_counts.keys():
            last_index = name_counts[child_name_str]
            current_index = last_index + 1
            child.name_indexed = f"{child_name_str}_{current_index}"
            name_counts[child_name_str] = current_index
        else:
            current_index = 0
            child.name_indexed = f"{child_name_str}_{current_index}"
            name_counts[child_name_str] = current_index


def add_index_all_init(root: "UniqueNode"):
    grouped_by_depth = group_by_depth(root)
    root.name_indexed = str(root.name)
    for _, nodes_with_same_depth in grouped_by_depth.items():
        for node in nodes_with_same_depth:
            node: UniqueNodeAddon = node
            add_index_to_duplicated_children_name_init(node)


class UniqueNodeAddon(Generic[NodeType]):
    name_indexed: str | None = None
    _name_unique: str | None = None

    @property
    def name_unique(self) -> str | None:
        if self.name_indexed is not None:
            if self._name_unique is None:
                self._name_unique = "/".join(
                    [str(node.name_indexed) for node in self.path]
                )
            return self._name_unique
        else:
            return None

    def __repr__(self):
        return _repr(self)

    def activate(self):
        root = self.path[0]
        add_index_all_init(root)


class UniqueNode(NodeMixin, UniqueNodeAddon):
    def __init__(self, name, parent=None, children=None, **kwargs):
        self.__dict__.update(kwargs)
        self.name = name
        self.parent = parent
        if children:
            self.children: Tuple[UniqueNode] = children

from anytree import PreOrderIter, NodeMixin


def print_root(root: NodeMixin):
    for node in PreOrderIter(root):
        print(node)

from anytree import AnyNode
from typing import List


class DictImporter:
    """
    An improved version of anytree.importer.DictImporter.

    This class allows importing tree structures from dictionary data with the ability
    to specify a custom key for child nodes.

    Args:
        chilren_name (str): Key name used to identify children in the dictionary. Defaults to "children".
        nodecls (class): Node class to be used for creating tree nodes. Defaults to AnyNode.

    Example:
        >>> importer = DictImporter()
        >>> data = {"name": "root", "children": [{"name": "child1"}, {"name": "child2"}]}
        >>> root = importer.import_(data)
    """

    def __init__(self, chilren_name="children", nodecls=AnyNode):
        self.nodecls = nodecls
        self.chilren_name = chilren_name

    def import_(self, data):
        """
        Import tree from dictionary data.

        Args:
            data (dict): Dictionary containing the tree structure.

        Returns:
            nodecls: Root node of the imported tree.
        """
        return self.__import(data)

    def __import(self, data, parent=None):
        attrs = dict(data)
        children = attrs.pop(self.chilren_name, [])
        node = self.nodecls(parent=parent, **attrs)
        for child in children:
            self.__import(child, parent=node)
        return node


class DictExporter:
    """
    Export tree structure to dictionary format.

    This class allows exporting tree nodes to dictionary format with the ability
    to specify which attributes to include and customize the key for child nodes.

    Args:
        chilren_name (str): Key name to use for children in the output dictionary. Defaults to "children".
        attrs (List[str]): List of attribute names to include in the export. If None, all attributes will be excluded
                          except those explicitly specified. Defaults to None.

    Example:
        >>> exporter = DictExporter(attrs=["name", "value"])
        >>> data = exporter.export(root_node)
    """

    def __init__(self, chilren_name="children", attrs: List[str] = None):
        self.chilren_name = chilren_name
        self.attriter = attrs

    def export(self, node):
        """
        Export tree to dictionary format.

        Args:
            node: Root node of the tree to export.

        Returns:
            dict: Dictionary representation of the tree.
        """
        return self._export(node)

    def _export(self, node):
        # Initialize dictionary with node attributes
        attrs = self._get_node_attributes(node)

        # Add children if they exist
        children = [self._export(child) for child in node.children]
        if children:
            attrs[self.chilren_name] = children

        return attrs

    def _get_node_attributes(self, node):
        """
        Extract the specified attributes from a node.

        Args:
            node: Node to extract attributes from.

        Returns:
            dict: Dictionary containing the node's attributes.
        """
        attrs = {}
        for name in dir(node):
            if name in self.attriter:
                if not name.startswith("_") and name != "parent" and name != "children":
                    value = getattr(node, name)
                    if not callable(value):
                        attrs[name] = value
        return attrs

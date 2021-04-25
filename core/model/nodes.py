import pandas as pd
from core.model.utils_nodes import node_exists, compute_distinct_nodes
from core.model.edges import *


class Nodes:

    def __init__(self, nodes: pd.DataFrame) -> None:
        """Constructor

        :param pd.DataFrame nodes: Set of all nodes
        """
        self.__nodes = nodes
        self.__distinct_nodes = None
        self.__stats = None

    @property
    def nodes(self) -> pd.DataFrame:
        """All nodes (label, type)

        :return: nodes
        :rtype: pd.DataFrame
        """
        return self.__nodes

    @nodes.setter
    def nodes(self, nodes: pd.DataFrame) -> None:
        self.__nodes = nodes

    @property
    def distinct_nodes(self) -> pd.DataFrame:
        """Method to get all distinct nodes

        :return: distinct_nodes (index=label+type)
        :rtype: pd.DataFrame
        """

        return self.__distinct_nodes

    def add_node(self, node: pd.Series, node_frequency) -> bool:
        """Method to add a new node to a set of existing nodes

        :param pd.Series node: The node to add to the set of existing nodes
        :param node_frequency: The frequency of the current node
        """
        node_id = str(node.loc['label']) + str(node.loc['type'])

        if node_exists(self.nodes, node_id) is False:
            self.__nodes.loc[node_id] = [node.loc['label'], node.loc['type'], node_frequency]
            return True
        else:
            return False

    def initialize_distinct_nodes(self, edges: pd.DataFrame) -> None:
        """Method to initialize the distinct nodes

        :param pd.DataFrame edges: The edges of the graph
        """
        self.__distinct_nodes = compute_distinct_nodes(self.__nodes, edges)

    def delete_node(self, node_id: str):
        """Method tot delete a node

        :param str node_id: The id of the node you want to delete
        """
        self.__nodes.drop(node_id, axis=0, inplace=True)

    def compute_reference_nodes(self, rm_graph_nodes: list) -> None:
        """Method to mark all reference model nodes in the graph

        :param list rm_graph_nodes: The set of all nodes which should be included in the rm_graph
        """

        number_of_columns = len(self.__nodes.columns)
        self.__nodes.insert(number_of_columns, "is_part_of_reference", False)

        for i in range(0, len(rm_graph_nodes)):
            current_node = rm_graph_nodes[i]

            self.__nodes.at[current_node, 'is_part_of_reference'] = True

    @property
    def node_stats(self) -> pd.Series:
        nodes_list = list(self.nodes['type'])
        if self.__stats is None and (len(nodes_list) >1 and type(nodes_list[0]) is not None):
            self.__stats = self.nodes.groupby('type').size()
            return self.__stats
        else:
            return self.__stats

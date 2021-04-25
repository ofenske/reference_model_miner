import pandas as pd
from core.model.utils_edges import compute_distinct_edges, edge_exists


class Edges:

    def __init__(self, edges: pd.DataFrame) -> None:
        """Constructor

        :param pd.DataFrame edges: Set of all edges
        """
        self.__edges = edges
        self.__distinct_edges = None
        self.__stats = None

    @property
    def edges(self) -> pd.DataFrame:
        """All edges (source, target, type)

        :return: edges
        :rtype: pd.DataFrame
        """
        return self.__edges

    @edges.setter
    def edges(self, edges: pd.DataFrame) -> None:
        self.__edges = edges

    @property
    def distinct_edges(self) -> pd.DataFrame:
        """Method to get all distinct edges

        :return: distinct_edges (index=source+target+type)
        :rtype: pd.DataFrame
        """

        return self.__distinct_edges

    def initialize_distinct_edges(self, nodes: pd.DataFrame, distinct_nodes: pd.DataFrame) -> None:
        """Method to compute the distinct edges of a graph

        :param pd.DataFrame nodes: The nodes of the graph
        :param distinct_nodes: The distinct nodes of the graph
        """
        self.__distinct_edges = compute_distinct_edges(self.edges, nodes, distinct_nodes)

    def add_edge(self, edge: pd.Series) -> bool:
        """Method to add an edge to an existing set of edges

        :param pd.Series edge: The edge to add
        """
        # get the id of the edge
        edge_id = edge.name

        # check if 'edge' already exists
        if edge_exists(self.edges, edge_id) is False:
            edge_source_node_id = str(edge.loc['source'].name)
            edge_target_node_id = str(edge.loc['target'].name)
            edge_type = edge.loc['type']
            edge_frequency = edge.loc['frequency']
            # add edge to 'edges'
            self.__edges.loc[edge_id] = [edge_source_node_id, edge_target_node_id, edge_type, edge_frequency]
            return True
        else:
            return False

    def delete_root_edges(self) -> None:
        """Method to delete all root edges of a graph
        """
        root_edges = self.__edges[self.__edges['type'] == 'root_edge']

        root_edges_index = list(root_edges.index)

        for i in range(0, len(root_edges)):
            current_root_edge_id = root_edges_index[i]
            self.__edges.drop(current_root_edge_id, axis=0, inplace=True)

    def delete_edge(self, edge_id: str):
        """ Method to delete an edge

        :param str edge_id: The edge of the edge you want to delete
        """
        self.__edges.drop(edge_id, axis=0, inplace=True)

    def compute_reference_edges(self, nodes: pd.DataFrame) -> None:
        """Method to mark all edges that should be in the final rm_graph

        :param pd.DataFrame nodes: The set of nodes that should be in the final rm_graph
        """

        # get the number of all columns in the edges DataFrame
        number_of_columns = len(self.__edges.columns)
        # insert new column ('is_part_of_reference') into edges DataFrame with False as default entries
        self.__edges.insert(number_of_columns, 'is_part_of_reference', False)

        # get a list of all node ids
        nodes_index = list(nodes.index)
        # get a list of all edge ids
        edges_index = list(self.edges.index)

        # iterate over all edges
        for i in range(0, len(edges_index)):
            # get the edge id
            edge_id = edges_index[i]
            # get source and target node of edge
            edge_source = self.edges.loc[edge_id]['source']
            edge_target = self.edges.loc[edge_id]['target']

            # check if source and target of edge are in the reference model
            if edge_source in nodes_index:
                if edge_target in nodes_index:
                    # add edge to reference model
                    self.__edges.at[edge_id, 'is_part_of_reference'] = True

    @property
    def edge_stats(self) -> pd.Series:
        """Getter for the statistics of all edges

        :return: The statistics of the edges
        :rtype: pd.Series
        """
        edge_list = list(self.edges['type'])
        if self.__stats is None and (len(edge_list) > 1 and type(edge_list[0]) is not None):
            self.__stats = self.edges.groupby('type').size()
            return self.__stats
        else:
            return self.__stats

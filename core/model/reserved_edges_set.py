import pandas as pd


class ReservedEdgesSet:

    def __init__(self) -> None:
        """Constructor

        """
        self.__reserved_edges_set = pd.DataFrame(columns=['source', 'target', 'type', 'source_node_id', 'frequency'])

    @property
    def reserved_edges_set(self) -> pd.DataFrame:
        return self.__reserved_edges_set

    def get_edge(self, edge_id: str) -> pd.Series:
        """Method to get a specific edge of 'reserved_edges_set'

        :param str edge_id: The id of the edge
        :return: Specific edge
        :rtype: pd.Series
        """
        return self.__reserved_edges_set.loc[edge_id]

    def get_relevant_edges(self, edge_source: str) -> pd.DataFrame:
        """Method to get all relevant edges according to their source_node

        :param str edge_source: The unique id of the source_node
        :return: A set of relevant edges
        :rtype: pd.DataFrame
        """
        return self.__reserved_edges_set[self.__reserved_edges_set['source_node_id'] == edge_source]

    def add_edge(self, edge: pd.Series) -> None:
        """Method to add an edge to 'reserved_edges_set'

        :param pd.Series edge: The edge to add
        """
        edge_id = edge.name
        edge_source_node = edge.loc['source']
        edge_target_node = edge.loc['target']
        edge_type = edge.loc['type']
        edge_source_node_id = str(edge.loc['source'].name)
        edge_frequency = edge.loc['frequency']
        self.__reserved_edges_set.loc[edge_id] = [edge_source_node, edge_target_node, edge_type, edge_source_node_id, edge_frequency]

    def delete_edge(self, edge_id: str) -> None:
        """Method to delete a specific edge out of 'reserved_edges_set'

        :param str edge_id: The index of the edge
        """
        self.__reserved_edges_set.drop(edge_id, axis=0, inplace=True)

import pandas as pd

from core.model.utils_nodes_set import distinct_node_exists


class NodesSet:

    def __init__(self) -> None:
        """Constructor

        """
        self.__nodes_set = pd.DataFrame(columns=['label', 'type', 'frequency', 'isRoot'])

    @property
    def nodes_set(self) -> pd.DataFrame:
        """

        :return:
        """
        return self.__nodes_set

    def get_node(self, node_label: str, node_type: str) -> pd.Series or None:
        """Method to query a special node out of nodes_set

        :param str node_label: The label of the node
        :param str node_type:  The type of the node
        :return: If node exists: result_node, Else: None
        :rtype: [pd.Series | None]
        """
        result_node = self.__nodes_set[
            (self.__nodes_set['label'] == node_label) & (self.__nodes_set['type'] == node_type)]

        if len(result_node) > 0:
            return result_node.iloc[0]

        else:
            return None

    def add_distinct_node(self, distinct_node: pd.Series) -> None:
        """Method to add a new node to the nodes_set

        :param pd.Series distinct_node: The node you want to add (label|type|frequency|isRoot)
        """
        # get the id of the distinct node
        distinct_node_id = distinct_node.name

        # check if 'distinct_node' already exists
        if distinct_node_exists(self.__nodes_set, distinct_node_id) is False:
            # get all the necessary attributes of 'distinct_node'
            distinct_node_label = distinct_node.loc['label']
            distinct_node_type = distinct_node.loc['type']
            distinct_node_frequency = distinct_node.loc['frequency']
            distinct_node_is_root = distinct_node.loc['isRoot']

            # add 'distinct_node' to 'nodes_set'
            self.__nodes_set.loc[distinct_node_id] = [distinct_node_label, distinct_node_type,
                                                      distinct_node_frequency, distinct_node_is_root]
        else:
            # update the frequency of 'distinct_node' in 'nodes_set'
            distinct_node_frequency = distinct_node.loc['frequency']
            new_frequency = float(self.__nodes_set.loc[distinct_node_id]['frequency']) + float(distinct_node_frequency)
            self.__nodes_set.at[distinct_node_id, 'frequency'] = new_frequency

import pandas as pd
import copy

from core.model.utils_edges_set import distinct_edge_exists, calculate_delete_costs, calculate_insert_costs, \
    calculate_move_costs, calculate_source_node_move_costs


class EdgesSet:

    def __init__(self) -> None:
        """Constructor

        :param pd.DataFrame edges_set: The set of unique edges
            source and target include the complete node as a pd.Series
        """
        self.__edges_set = pd.DataFrame(columns=['source', 'target', 'type', 'frequency', 'cost_value'])

    @property
    def edges_set(self) -> pd.DataFrame:
        """Method to get the edges_set

        :return: edges_set
        :rtype: pd.DataFrame
        """
        return self.__edges_set

    def get_most_frequent_edge(self) -> pd.Series:
        """Method to get the edge with the highest value for 'cost_value'

        :return: most_frequent_edge
        :rtype: pd.Series
        """
        # get the most frequent edges according to the cost_value
        most_frequent_edges = self.__edges_set[self.__edges_set['cost_value'] == self.__edges_set['cost_value'].max()]

        # check if there is a most frequent edge
        if len(most_frequent_edges) is 0:
            return None
        else:
            most_frequent_edge = copy.deepcopy(most_frequent_edges.iloc[0])

            return most_frequent_edge

    def init_cost_value(self, edge_id: str, insert_cost: float, move_cost: float,
                        delete_cost: float, target_node_frequency: float) -> None:
        """Method to initialize the cost_value for an edge

        :param str edge_id: The id of the edge we want to update
        :param float insert_cost: The insert costs
        :param float move_cost: The move costs
        :param float delete_cost: The delete costs
        :param float target_node_frequency: The frequency of the target node of 'edge'
        """
        # calculate the different costs for 'edge'
        edge_frequency = float(self.__edges_set.loc[edge_id]['frequency'])
        insert_costs = float(calculate_insert_costs(target_node_frequency, insert_cost))
        move_costs = float(calculate_move_costs(target_node_frequency, edge_frequency, move_cost))
        delete_costs = float(calculate_delete_costs(edge_frequency, delete_cost))

        # get the edge type
        edge_type = self.__edges_set.loc[edge_id]['type']

        # check if the 'edge_type' is root_edge
        # based on that, calculate the move_cost for the source node of 'edge'
        if edge_type is 'root_edge':
            source_node_move_costs = float(calculate_source_node_move_costs(True, edge_frequency, move_cost))
        else:
            source_node_move_costs = float(calculate_source_node_move_costs(False, edge_frequency, move_cost))

        # calculate the new cost_value for 'edge'
        cost_value = float(insert_costs - move_costs - delete_costs - source_node_move_costs)

        # set new cost_value for 'edge'
        self.__edges_set.at[edge_id, 'cost_value'] = cost_value

    def delete_edge(self, edge_id: str) -> None:
        """Method to delete a specific edge

        :param str edge_id: The index of the edge
        """

        self.__edges_set.drop(edge_id, axis=0, inplace=True)

    def add_distinct_edge(self, distinct_edge: pd.Series) -> None:
        """Method to add a new distinct edge to the edges_set

        :param pd.Series distinct_edge: The edge you want to add (source|target|type|frequency|cost_value)
            source and target include the complete node as a pd.Series
        """
        # get the id of the distinct edge
        distinct_edge_id = distinct_edge.name

        # check if 'distinct_edge' already exists in 'edges_set'
        if distinct_edge_exists(self.__edges_set, distinct_edge_id) is False:
            # get source and target node of 'distinct_edge' (as pd.Series)
            distinct_edge_source_node = distinct_edge.loc['source']
            distinct_edge_target_node = distinct_edge.loc['target']

            # get type and frequency of 'distinct_edge'
            distinct_edge_type = distinct_edge.loc['type']
            distinct_edge_frequency = distinct_edge.loc['frequency']

            # insert 'distinct_edge' into 'edges_set'
            self.__edges_set.loc[distinct_edge_id] = [distinct_edge_source_node, distinct_edge_target_node,
                                                      distinct_edge_type, distinct_edge_frequency, None]
        else:
            distinct_edge_frequency = distinct_edge.loc['frequency']
            new_frequency = float(self.__edges_set.loc[distinct_edge_id]['frequency']) + float(distinct_edge_frequency)
            # update the frequency of 'distinct_edge' in 'edges_set'
            self.__edges_set.at[distinct_edge_id, 'frequency'] = new_frequency

    def update_cost_value(self, source_node_id: str, move_cost: float) -> None:
        """Method to update the cost_value for specific edges in 'edges_set'

        :param str source_node_id: The id of the node, which was newly added to rm_graph
        :param float move_cost: The move costs
        """
        edges_set_index = list(self.edges_set.index)

        # iterate through all edges in 'edges_set'
        for i in range(0, len(edges_set_index)):
            # get attributes for the current_edge
            current_edge_id = edges_set_index[i]
            current_edge = self.edges_set.loc[current_edge_id]
            current_edge_source_node_id = current_edge.loc['source'].name
            current_edge_frequency = current_edge.loc['frequency']

            # check if 'current_edge_source_node_id' is equals 'source_node_id'
            if current_edge_source_node_id is source_node_id:
                # update the cost_value of 'current_edge' in 'edges_set'
                new_cost_value = float(current_edge.loc['cost_value']) + float((current_edge_frequency * move_cost))
                self.__edges_set.at[current_edge_id, 'cost_value'] = new_cost_value



import pandas as pd


def distinct_edge_exists(edges_set: pd.DataFrame, edge_id: str) -> bool:
    """Method to evaluate if a node already exists

    :param pd.Series edges_set: All distinct edges
    :param pd.Series edge_id: The unique id of the edge
    :return: True | False
    :rtype: bool
    """

    edges_set_index = list(edges_set.index)

    if edge_id in edges_set_index:
        return True
    else:
        return False


def calculate_move_costs(target_node_frequency: float, edge_frequency: float, move_cost: float) -> float:
    """Method to compute the costs of move operation for an edge

    :param float target_node_frequency: The frequency of the target node of the edge
    :param float edge_frequency: The frequency of the edge
    :param move_cost: The cost for move operation
    :return: move_costs
    :rtype: float
    """
    move_costs = float((target_node_frequency - edge_frequency) * move_cost)

    return move_costs


def calculate_delete_costs(edge_frequency: float, delete_cost: float) -> float:
    """Method to compute the costs of delete operation for an edge

    :param float edge_frequency: The frequency of the edge
    :param float delete_cost: The cost for delete operation
    :return: delete_costs
    :rtype: float
    """
    delete_costs = float((1 - edge_frequency) * delete_cost)

    return delete_costs


def calculate_source_node_move_costs(source_node_is_added: bool, edge_frequency: float, move_cost: float) -> float:
    """Method to compute the costs of source-node-move operation for an edge

    :param bool source_node_is_added: True if source_node already in rm_graph
    :param float edge_frequency: The frequency of the edge
    :param move_cost: The cost for delete operation
    :return: source_node_move_costs
    :rtype: float
    """
    if source_node_is_added is True:
        return 0
    else:
        return float(edge_frequency * move_cost)


def calculate_insert_costs(target_node_frequency: float, insert_cost: float) -> float:
    """Method to compute the costs of insert operation for an edge

    :param float target_node_frequency: The frequency of the target node of the edge
    :param float insert_cost: The cost for delete operation
    :return: insert_costs
    :rtype: float
    """
    return float(target_node_frequency * insert_cost)

import pandas as pd


def distinct_node_exists(nodes_set: pd.DataFrame, node_id: str) -> bool:
    """Method to evaluate if a node already exists

    :param nodes_set: Set of all nodes
    :param str node_id: The id of the node
    :return: True|False
    :rtype: bool
    """
    nodes_index = list(nodes_set.index)

    if node_id in nodes_index:
        return True
    else:
        return False

from core.model.edges import *


def compute_distinct_nodes(nodes: pd.DataFrame, edges: pd.DataFrame) -> pd.DataFrame:
    """Method to compute all distinct nodes out of a set of nodes

    :return: distinct_nodes
    :rtype: pd.DataFrame (index = label+type)
    """
    # get the columns for the distinct nodes
    columns = list(nodes) + ['frequency', 'isRoot']
    unique_nodes_set = pd.DataFrame(columns=columns)

    # iterate over all nodes in 'nodes'
    for i in range(0, len(nodes)):
        # get all necessary attributes of 'current_node'
        current_node = nodes.iloc[i]
        current_node_id = current_node.name
        current_node_index = str(current_node.loc['label']) + str(current_node.loc['type'])

        # check if 'current_node' is already in 'unique_nodes_set'
        if current_node_index in list(unique_nodes_set.index):
            # update frequency of 'current_node' in 'unique_nodes_set'
            new_frequency = float(unique_nodes_set.loc[current_node_index]['frequency']) + float(1.0)
            unique_nodes_set.at[current_node_index, 'frequency'] = new_frequency

        # check if 'current_node' is not already in 'unique_nodes_set'
        elif current_node_index not in list(unique_nodes_set.index):
            # add 'current_node' to 'unique_nodes_set'
            current_node_is_root_node = is_root_node(current_node_id, edges)
            unique_nodes_set.loc[current_node_index] = [current_node.loc['label'], current_node.loc['type'], 1,
                                                        current_node_is_root_node]

    return unique_nodes_set


def node_exists(nodes: pd.DataFrame, node_id: str) -> bool:
    """Method to evaluate if a node already exists

    :param nodes: Set of all nodes
    :param str node_id: The id of the node
    :return: True|False
    :rtype: bool
    """
    nodes_index = list(nodes.index)

    if node_id in nodes_index:
        return True
    else:
        return False


def is_root_node(node_id: str, edges: pd.DataFrame) -> bool:
    """Method to check if a node is a root node

    :param node_id:
    :param edges:
    :return:
    """
    # get all edges where the specific node is a target_node
    relevant_edges = edges[edges['target'] == node_id]

    # check if the specific node is a target node in one or more edges
    if len(relevant_edges) > 0:
        return False
    else:
        return True

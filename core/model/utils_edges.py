import pandas as pd


def compute_distinct_edges(edges: pd.DataFrame, nodes: pd.DataFrame, distinct_nodes: pd.DataFrame) -> pd.DataFrame:
    """Method to compute the distinct edges for Edges

    :param pd.DataFrame edges: The set of all edges of a graph
    :param pd.DataFrame nodes: The set of all nodes of a graph
    :param pd.DataFrame distinct_nodes: The set of all distinct nodes of a graph
    :return: A set of distinct edges
    :rtype: pd.DataFrame
    """
    # initialize the set for the unique edges
    unique_edges_set = pd.DataFrame(columns=['source', 'target', 'type', 'frequency'])

    # iterate over all edges in 'edges'
    for i in range(0, len(edges)):
        # get all necessary attributes of the current_edge
        current_edge = edges.iloc[i]
        try:
            current_edge_source = nodes.loc[current_edge.loc['source']]
        except KeyError:
            break
        current_edge_target = nodes.loc[current_edge.loc['target']]
        current_edge_source_id = str(current_edge_source.loc['label']) + str(current_edge_source.loc['type'])
        current_edge_target_id = str(current_edge_target.loc['label']) + str(current_edge_target.loc['type'])
        current_edge_source_node = distinct_nodes.loc[current_edge_source_id]
        current_edge_target_node = distinct_nodes.loc[current_edge_target_id]
        current_edge_type = str(current_edge.loc['type'])
        current_edge_id = str(current_edge_source_id) + str(current_edge_target_id) + str(current_edge_type)

        # check if 'current_edge' is not already in 'unique_edges_set'
        if current_edge_id not in list(unique_edges_set.index):

            # exception handling
            try:
                # add 'current_edge' to 'unique_edges_set'
                unique_edges_set.loc[current_edge_id] = [current_edge_source_node, current_edge_target_node,
                                                         current_edge_type, 1]
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                else:
                    print(e)

        # check if 'current_edge' is already in 'unique_edges_set'
        elif current_edge_id in list(unique_edges_set.index):
            # update the frequency of 'current_edge' in 'unique_edges_set'
            new_frequency = float(unique_edges_set.loc[current_edge_id]['frequency']) + float(1.0)
            unique_edges_set.at[current_edge_id, 'frequency'] += new_frequency

    return unique_edges_set


def compute_nodes_ids(edge_source_node: pd.Series, edge_target_node: pd.Series,
                      nodes: pd.DataFrame) -> list:
    """Method to compute the node_ids of source and target node of an edge

    :param pd.Series edge_source_node: Source node
    :param pd.Series edge_target_node: Target node
    :param pd.DataFrame nodes: Set of all nodes of the graph
    :return: [edge_source, edge_target]
    :rtype: list
    """
    edge_source_node_label = edge_source_node.loc['label']
    edge_source_node_type = edge_source_node.loc['type']
    edge_target_node_label = edge_target_node.loc['label']
    edge_target_node_type = edge_target_node.loc['type']

    edge_source = \
        list(nodes[(nodes['label'] == edge_source_node_label) & (nodes['type'] == edge_source_node_type).index])[0]

    edge_target = \
        list(nodes[(nodes['label'] == edge_target_node_label) & (nodes['type'] == edge_target_node_type).index])[0]

    return [edge_source, edge_target]


def edge_exists(edges: pd.DataFrame, edge_id: str) -> bool:
    """Method to check if an edge already exists.

    :param pd.DataFrame edges: The set of all edges
    :param edge_id: The id of an edge
    :return: True|False
    :rtype: bool
    """
    edges_index = list(edges.index)

    if edge_id not in edges_index:
        return False
    else:
        return True

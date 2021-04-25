import pandas as pd
import copy


def compute_node_index(nodes: pd.DataFrame, node_id: str) -> str:
    """Method to compute the unique index of a node (label+type)

    :param pd.DataFrame nodes: Set of all nodes
    :param node_id: The id of the node for which you want to compute the new index
    :return: node_id
    :rtype: str
    """

    node = nodes.loc[node_id]
    node_label = node.loc['label']
    node_type = node.loc['type']
    node_index = str(node_label) + str(node_type)

    return node_index


def compute_connectivity(cluster_nodes: list, edges: pd.DataFrame) -> float:
    """Method to compute the connectivity for one cluster in one input model

    :param list cluster_nodes: The set of nodes of one cluster
    :param pd.DataFrame edges: The set of all edges of the input graph
    :return: connectivity
    :rtype: float
    """
    communities = detect_communities(cluster_nodes, edges)
    return 1 / len(communities)


def detect_communities(cluster_nodes: list, edges: pd.DataFrame) -> list:
    """Method to detect communities for one cluster.

    :param list cluster_nodes: A list of all node_ids of the nodes in the cluster
    :param pd.DataFrame edges: The set of all edges of the input graph
    :return: communities (list of lists)
    :rtype: list
    """
    relevant_nodes = copy.copy(cluster_nodes)
    communities = []
    while len(relevant_nodes) > 0:
        community = detect_community(relevant_nodes, edges)
        communities.append(community)
        for node in community:
            relevant_nodes.remove(node)
    return communities


def detect_community(cluster_nodes: list, edges: pd.DataFrame) -> list:
    """Method to detect one community in a cluster.

    :param list cluster_nodes: A list of all node_ids of the nodes in the cluster
    :param pd. DataFrame edges: The set of all edges of the input graph
    :return: community (set of node_ids)
    :rtype: list
    """
    community = []
    visited = []
    current_node = cluster_nodes[0]
    visited.append(current_node)

    while len(visited) > 0:
        current_node = visited[0]
        neighbours = compute_neighbours(edges, current_node)
        for i in range(0, len(neighbours)):
            current_neighbour = neighbours[i]
            if current_neighbour not in visited and current_neighbour not in community and current_neighbour in cluster_nodes:
                visited.append(current_neighbour)

        community.append(copy.copy(visited[0]))
        del (visited[0])

    return community


def compute_neighbours(edges: pd.DataFrame, current_node_id: str) -> list:
    """Method to compute the neighbours of a node

    :param pd.DataFrame edges: The set of all edges of the input graph
    :param str current_node_id: The id of the node for which you want compute the neighbours
    :return: relevant_nodes (set of neighbour node ids)
    :rtype: list
    """
    relevant_edges = edges[(edges['source'] == current_node_id) | (edges['target'] == current_node_id)]
    relevant_nodes = []
    for i in range(0, len(relevant_edges)):
        current_edge = relevant_edges.iloc[i]
        if current_edge.loc['source'] == current_node_id:
            relevant_nodes.append(current_edge.loc['target'])
        else:
            relevant_nodes.append(current_edge.loc['source'])

    return relevant_nodes


def compute_high_level_nodes(nodes: pd.DataFrame, edges: pd.DataFrame, node_type: str = False) -> list:
    """Method to compute the high level nodes of a graph (all nodes which have no parents)

    :param pd.DataFrame nodes: The set of nodes of the graph
    :param pd.DataFrame edges: The set of edges of the graph
    :param str node_type: The type of node which should be considered as high level nodes
    :return: A list with all node ids of the high level nodes
    :rtype: list
    """
    # initialize empty list for high level nodes
    high_level_nodes = []
    # iterate over all nodes
    nodes_index = list(nodes.index)
    if not node_type:
        for node_index in nodes_index:
            # compute all edges which has 'node' as their target
            relevant_edges = edges[edges['target'] == node_index]
            # if there is no edge in 'relevant_edges' the current 'node' have to be a high level node
            if len(relevant_edges) is 0:
                # add 'node' to 'high_level_nodes'
                high_level_nodes.append(node_index)
    else:
        for node_index in nodes_index:
            # only nodes of specified types are considered as high level nodes
            if nodes.loc[node_index]['type'] != node_type:
                continue
            # compute all edges which has 'node' as their target
            relevant_edges = edges[edges['target'] == node_index]
            # if there is no edge in 'relevant_edges' the current 'node' have to be a high level node
            if len(relevant_edges) is 0:
                # add 'node' to 'high_level_nodes'
                high_level_nodes.append(node_index)

    return high_level_nodes


def compute_child_nodes(high_level_node: str, edges: pd.DataFrame) -> list:
    """Method to compute the child nodes of a specific node

    :param high_level_node: The node for which one want to compute the children
    :param edges: The set of all edges of the graph
    :return: A list with all ids of the child nodes
    :rtype: list
    """
    # initialize empty list for child nodes
    child_nodes = []
    # initialize queue for the nodes for which we have to compute the children
    # (child of a child is also a child of 'high_level_node')
    visited_nodes = [high_level_node]
    # do computation until 'visited_nodes' is empty
    while len(visited_nodes) > 0:
        # get the current node
        current_node = visited_nodes.pop(0)
        # compute all edges which has 'current_node' as their source
        relevant_edges = edges[edges['source'] == current_node]
        if len(relevant_edges) > 0:
            # iterate over all edges in 'relevant_edges'
            relevant_edges_ids = list(relevant_edges.index)
            for edge_id in relevant_edges_ids:
                # get the target of 'edge' (which is the child of 'high_level_node')
                child_node = relevant_edges.loc[edge_id]['target']
                # check if 'child_node' is not already in 'child_nodes'
                if child_node not in child_nodes:
                    child_nodes.append(child_node)
                    visited_nodes.append(child_node)

    return child_nodes

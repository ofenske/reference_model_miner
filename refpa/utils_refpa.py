from core.model.graph import *


def compute_common_nodes(nodes_set: pd.DataFrame) -> list:
    """Method to compute the common nodes out of the nodes of all input models

    :param pd.DataFrame nodes_set: The set of the nodes of all input models
    :return: common_nodes (list of unique node_ids(label+type)
    :rtype: list
    """
    common_nodes_dataframe = nodes_set[nodes_set['frequency'] == 1.0]

    common_nodes = list(common_nodes_dataframe.index)

    return common_nodes


def compute_clusters_for_all_input_graphs(graphs_set: list) -> None:
    """Method to compute the nodes clusters for all input graphs

    :param list graphs_set: A set of all input graphs
    """
    for graph in graphs_set:
        graph.compute_nodes_clusters()


def evaluate_clusters(graphs_set: list) -> pd.DataFrame:
    """Method to evaluate the clusters of all input graphs

    :param list graphs_set: The set with all input graphs in it
    """
    # initialize the clusters for the 'rm_graph'
    rm_clusters = pd.DataFrame(columns=['nodes', 'evaluation_metric'])

    # iterate over all graphs in 'graphs_set'
    for graph in graphs_set:
        # get clusters of the current graph
        graph_clusters = graph.nodes_clusters
        # get a list of indexes of the clusters of the current graph
        graph_clusters_index = list(graph_clusters.index)

        # iterate over all clusters of the current graph
        for i in range(0, len(graph_clusters_index)):
            # get the index of the current cluster
            cluster_index = graph_clusters_index[i]

            # get the indexes of all clusters which are already in 'rm_clusters' included
            rm_clusters_index = list(rm_clusters.index)

            # get the nodes and the connectivity of the current cluster
            cluster_nodes = graph_clusters.loc[cluster_index]['nodes']
            evaluation_metric = graph_clusters.loc[cluster_index]['evaluation_metric']

            # check if the current cluster is not already in 'rm_cluster'
            if cluster_index not in rm_clusters_index:
                # insert current cluster as a new cluster in 'rm_clusters'
                rm_clusters.loc[cluster_index] = [cluster_nodes, evaluation_metric]

            # check if the current cluster is already in 'rm_cluster'
            elif cluster_index in rm_clusters_index:
                # check if the connectivity of current cluster is higher then the connectivity of the same cluster
                # which is already in 'rm_graph' included
                if evaluation_metric > rm_clusters.loc[cluster_index]['evaluation_metric']:
                    # set the nodes and the connectivity of the current cluster as the new values of the'rm_graph' cluster
                    rm_clusters.at[cluster_index, 'nodes'] = cluster_nodes
                    rm_clusters.at[cluster_index, 'evaluation_metric'] = evaluation_metric

    return rm_clusters


def compute_rm_graph_nodes(common_nodes: list, rm_clusters: pd.DataFrame) -> list:
    """Method to compute the nodes which should be in the final rm_graph

    :param list common_nodes: The list of common nodes
    :param pd.DataFrame rm_clusters: Set with all distinct clusters in it
    :return: rm_graph_nodes
    :rtype: list
    """

    rm_graph_nodes = common_nodes

    rm_clusters_index = list(rm_clusters.index)
    for i in range(0, len(rm_clusters_index)):
        current_cluster_id = rm_clusters_index[i]
        current_cluster_nodes = rm_clusters.loc[current_cluster_id]['nodes']

        for j in range(0, len(current_cluster_nodes)):
            if current_cluster_nodes[j] not in rm_graph_nodes:
                rm_graph_nodes.append(current_cluster_nodes[j])

    return rm_graph_nodes


def create_final_rm_graph(rm_graph_nodes: list, rm_graph: Graph) -> None:
    """Method to create the final rm_graph

    :param list rm_graph_nodes: The set with all node_ids of the nodes which should be in the final rm_graph
    :param Graph rm_graph: The initial rm_graph
    """

    # compute and mark all nodes which should be in the final rm_graph
    rm_graph.compute_reference_nodes(rm_graph_nodes)

    rm_graph_nodes_index = list(rm_graph.nodes.index)
    # delete all non-reference nodes out of rm_graph
    for i in range(0, len(rm_graph_nodes_index)):
        current_node_id = rm_graph_nodes_index[i]
        if rm_graph.nodes.loc[current_node_id]['is_part_of_reference'] == False:
            rm_graph.delete_node(current_node_id)

    # compute and all edges which should be in the final rm_graph
    rm_graph.compute_reference_edges()

    rm_graph_edges_index = list(rm_graph.edges.index)
    # delete all non-reference edges out of rm_graph
    for i in range(0, len(rm_graph_edges_index)):
        current_edge_id = rm_graph_edges_index[i]
        if rm_graph.edges.loc[current_edge_id]['is_part_of_reference'] == False:
            rm_graph.delete_edge(current_edge_id)

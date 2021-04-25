import pandas as pd
import copy
import numpy as np
from core.model.utils_nodes_clusters import compute_node_index, compute_connectivity, compute_high_level_nodes, \
    compute_child_nodes


class NodesClusters:

    def __init__(self):
        """Constructor

        """
        self.__nodes_clusters = pd.DataFrame()

    @property
    def nodes_clusters(self) -> pd.DataFrame:
        """ Method to get all nodes clusters of the graph

        :return: nodes_clusters
        :rtype: pd.DataFrame
        """
        return self.__nodes_clusters

    def compute_nodes_clusters(self, nodes: pd.DataFrame) -> None:
        """ Method to compute the nodes_clusters for a graph. Cluster criteria is the type of the nodes.

        :param pd.DataFrame nodes: The set of all nodes of the graph
        """
        self.__nodes_clusters['nodes'] = None
        self.__nodes_clusters['evaluation_metric'] = None

        # get all node types
        unique_node_types = nodes.drop_duplicates('type').loc[:, 'type'].values

        # iterate over all node types
        for i in range(len(unique_node_types)):
            # get current node type
            current_node_type = unique_node_types[i]

            # check special case if the node has no type ('nan')
            if type(current_node_type) is float and np.isnan(current_node_type):
                # get all node ids with 'nan' as their type
                relevant_nodes_ids = list(nodes[(nodes['label'].isnull()) | (nodes['type'].isnull())].index)

            else:
                # get all node ids with 'current_node_type' as their type
                relevant_nodes_ids = list(nodes[nodes['type'] == current_node_type].index)

            # append all nodes of type 'current_node_type' to 'nodes_clusters'
            self.__nodes_clusters.loc[current_node_type] = [relevant_nodes_ids, None]

    def compute_cluster_connectivities(self, edges: pd.DataFrame) -> None:
        """Method to compute and set the connectivities of all clusters in the graph

        :param pd.DataFrame edges: The set of all edges of the graph.
        """
        # get all ids of nodes_clusters
        nodes_clusters_index = list(self.__nodes_clusters.index)

        # iterate over all clusters in 'nodes_clusters'
        for i in range(0, len(nodes_clusters_index)):
            # get the index of the current cluster
            current_cluster_index = nodes_clusters_index[i]
            # get all node ids of the current cluster
            current_cluster_nodes = self.nodes_clusters.loc[current_cluster_index]['nodes']

            # compute the connectivity of the current cluster
            current_cluster_connectivity = compute_connectivity(current_cluster_nodes, edges)

            # set the connectivity of the current cluster in 'nodes_clusters'
            self.__nodes_clusters.at[current_cluster_index, 'evaluation_metric'] = current_cluster_connectivity

    def update_node_ids(self, nodes: pd.DataFrame) -> None:
        """Method to update the node_ids of the nodes in the single clusters to the unique node_ids (label+type)

        :param pd.DataFrame nodes: The set of all nodes of the graph
        """
        # get all ids of nodes_clusters
        node_clusters_index = list(self.__nodes_clusters.index)

        # iterate over all clusters in 'nodes_clusters'
        for i in range(0, len(node_clusters_index)):
            # get the name of the current cluster
            cluster_name = node_clusters_index[i]
            # get the nodes of the current cluster
            cluster_nodes = self.__nodes_clusters.loc[cluster_name]['nodes']

            # initiate an empty list for the new ids of nodes
            new_cluster_nodes = []

            # iterate over all nodes in the cluster to update their ids
            for j in range(0, len(cluster_nodes)):
                new_cluster_nodes.append(compute_node_index(nodes, cluster_nodes[j]))

            # set the list with the new node ids in 'nodes_clusters'
            self.__nodes_clusters.at[cluster_name, 'nodes'] = new_cluster_nodes

    def cluster_by_high_level_nodes(self, nodes: pd.DataFrame, edges: pd.DataFrame) -> None:
        self.__nodes_clusters['nodes'] = None
        self.__nodes_clusters['evaluation_metric'] = None

        high_level_nodes = compute_high_level_nodes(nodes, edges)

        for high_level_node in high_level_nodes:
            child_nodes = compute_child_nodes(high_level_node, edges)
            updated_child_nodes = []
            for child_node in child_nodes:
                updated_child_nodes.append(compute_node_index(nodes, child_node))
            high_level_node_id = compute_node_index(nodes, high_level_node)
            updated_child_nodes.append(high_level_node_id)
            self.__nodes_clusters.loc[high_level_node_id] = [updated_child_nodes, len(updated_child_nodes)]

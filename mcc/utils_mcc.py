from core.model.graph import *
from core.model.edges_set import *
from core.model.nodes_set import *
from core.model.reserved_edges_set import *


def update_nodes_set(graph: Graph, nodes_set: pd.DataFrame) -> None:
    """Method to update the nodes_set with new nodes

    :param Graph graph: The graph from which you want to add the nodes to the nodes_set
    :param pd.DataFrame nodes_set: The nodes_set where you want to add new nodes
    """
    # iterate through all distinct nodes of an graph and add this node to the nodes_set if it doesn't exist else update the frequency
    distinct_graph_nodes = graph.distinct_nodes
    distinct_graph_nodes_index = list(distinct_graph_nodes.index)
    for i in range(0, len(distinct_graph_nodes_index)):
        current_node_id = distinct_graph_nodes_index[i]
        current_node = distinct_graph_nodes.loc[current_node_id]
        nodes_set.add_distinct_node(current_node)


def update_edges_set(graph: Graph, edges_set: pd.DataFrame) -> None:
    """Method to update the edges_set with new edges

    :param Graph graph: The graph from which you want to add the edges to the edges_set
    :param pd.DataFrame edges_set: The edges_set where you want to add new edges
    """
    # get all distinct edges of 'graph'
    distinct_graph_edges = graph.distinct_edges
    # get the index of 'distinct_graph_edges'
    distinct_graph_edges_index = list(distinct_graph_edges.index)

    # iterate through all edges in 'distinct_graph_edges' and add them to 'edges_set'
    for i in range(0, len(distinct_graph_edges_index)):
        current_edge_id = distinct_graph_edges_index[i]
        current_edge = distinct_graph_edges.loc[current_edge_id]
        edges_set.add_distinct_edge(current_edge)


def initialize_cost_values(edges_set: EdgesSet, nodes_set: NodesSet, move_cost: float, insert_cost: float,
                           delete_cost: float) -> None:
    """Method to initialize the cost_value for all edges of the edges_set

    :param pd.DataFrame edges_set: The edges_set for which you want to initialize te cost_values
    :param pd.DataFrame nodes_set: The set of all nodes of the edges
    :param float move_cost: Cost to do move operation
    :param float insert_cost: Cost to do insert operation
    :param float delete_cost: Cost to do delete operation
    """
    # get the index of 'edges_set'
    edges_set_index = list(edges_set.edges_set.index)

    # iterate through all edges in 'edges_set' to compute the initial cost_values for all edges
    for i in range(0, len(edges_set_index)):
        # get the id of the current edge
        current_edge_id = edges_set_index[i]
        # get the frequency and id of the target node of the current edge
        target_node = edges_set.edges_set.loc[current_edge_id]['target']
        target_node_id = str(target_node.loc['label']) + str(target_node.loc['type'])
        target_node_frequency = nodes_set.nodes_set.loc[target_node_id]['frequency']

        # compute and set the cost value for current edge
        edges_set.init_cost_value(current_edge_id, insert_cost, move_cost, delete_cost, target_node_frequency)


def compute_artificial_edges(nodes_set: pd.DataFrame, edges_set: pd.DataFrame) -> None:
    """Method to compute the artificial edges for all root_nodes

    :param pd.DataFrame nodes_set: The set of all nodes of the edges
    :param pd.DataFrame edges_set: The edges_set where you want to add the artificial edges
    """
    # get all root_nodes out of 'nodes_set'
    root_nodes = nodes_set[nodes_set['isRoot'] == True]

    # iterate through all nodes in 'root_nodes' to construct for every root node an artificial edge
    for i in range(0, len(root_nodes)):
        current_root_node = root_nodes.iloc[i]
        # compute the edge id for the artificial edge
        artificial_edge_id = "None" + current_root_node.loc['label'] + current_root_node.loc['type'] + "root_edge"
        # get the frequency of 'current_root_node'
        current_root_node_frequency = float(current_root_node.loc['frequency'])
        # build pd.Series for 'current_root_node'
        none_nodes = pd.DataFrame.from_dict({'NoneNone': [None, None]}, orient='index', columns=['label', 'type'])
        none_node = none_nodes.iloc[0]

        # append the artificial_edge to 'edges_set' and set 'current_root_node_frequency' as the frequency for the new edge
        edges_set.loc[artificial_edge_id] = [none_node, current_root_node, 'root_edge', current_root_node_frequency,
                                             None]


def check_graph_for_all_reserved_edges(reserved_edges_set: ReservedEdgesSet, rm_graph: Graph) -> None:
    """Method to check for all edges in 'reserved_edges_set' if they could be added to rm_graph

    :param ReservedEdgesSet reserved_edges_set: The set of reserved edges
    :param rm_graph: The graph where you want to add the new edges
    """
    reserved_new_edges = reserved_edges_set.reserved_edges_set

    # iterate through all edges in 'reserved_new_edges'
    for i in range(0, len(reserved_new_edges)):
        new_candidate_edge = reserved_new_edges.iloc[i]
        # get the id of the source node of 'new_candidate_edge'
        new_candidate_edge_source_node_id = new_candidate_edge.loc['source'].name

        # check if 'new_candidate_edge_source_node_id'
        if rm_graph.node_exists(new_candidate_edge_source_node_id) is True:
            # add 'new_candidate_edge' to 'rm_graph'
            rm_graph.add_edge(new_candidate_edge)
            # add 'new_candidate_edge' to 'rm_graph'
            new_edge_target_node = new_candidate_edge.loc['target']
            frequency = new_edge_target_node['frequency']
            rm_graph.add_node(new_edge_target_node,frequency)


def check_graph_for_relevant_reserved_edges(reserved_edges_set: ReservedEdgesSet, new_edge_target_node_id: str,
                                            rm_graph: Graph) -> None:
    """Method to check for specific edges in 'reserved_edges_set' if they could be added to rm_graph

    :param ReservedEdgesSet reserved_edges_set: The set of reserved edges
    :param new_edge_target_node_id:
    :param rm_graph: The graph where you want to add the new edges
    """
    # get the relevant edges
    reserved_new_edges = reserved_edges_set.get_relevant_edges(new_edge_target_node_id)

    # add all edges of 'reserved_new_edges' to 'rm_graph'
    for i in range(0, len(reserved_new_edges)):
        new_edge = copy.deepcopy(reserved_new_edges.iloc[i])
        rm_graph.add_edge(new_edge)
        new_edge_target_node = new_edge.loc['target']
        frequency = new_edge_target_node['frequency']
        rm_graph.add_node(new_edge_target_node, frequency)
        reserved_edges_set.delete_edge(str(new_edge.name))

    def get_node_frequency(self, node: Nodes) -> float:
        """Method to get the  frequency of a Nodes object

        :return: frequency: the frequency of the current node
        :rtype: float
        """
        # compute the id of the node
        node_id = str(node.loc['label']) + str(node.loc['type'])
        # get the frequency from the nodes_set
        frequency = self.nodes_set.loc[node_id]['frequency']
        return frequency

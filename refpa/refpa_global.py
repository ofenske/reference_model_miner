from mcc.mcc_global import *
from refpa.utils_refpa import compute_common_nodes, compute_clusters_for_all_input_graphs, evaluate_clusters, \
    compute_rm_graph_nodes, create_final_rm_graph


class RefPaGlobal:

    def __init__(self, path: str) -> None:
        """Constructor

        :param str path: relative path to directory where the xml files for the input models are located
        """
        self.__path = path
        self.__rm_graph = None
        self.__graphs_set = []
        self.__common_nodes = []
        self.__rm_clusters = pd.DataFrame(columns=['nodes', 'connectivity'])
        self.__rm_graph_nodes = []

        # set the parameters of the mcc_algorithm
        mcc_move_cost = float(2.0)
        mcc_delete_cost = float(1.0)
        mcc_insert_cost = float(10.0)
        mcc_threshold = -100.0
        # execute mcc algorithm to merge all input models into one model
        self.__mcc_algorithm = MCCGlobal(self.path, mcc_move_cost, mcc_delete_cost, mcc_insert_cost, mcc_threshold)

    @property
    def path(self) -> str:
        """Method to get the path where the files for the input models are located

        :return: path
        :rtype: str
        """
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        self.__path = str(path)

    @property
    def rm_graph(self) -> Graph:
        """Method to get the final reference graph

        :return: rm_graph
        :rtype: Graph
        """
        return self.__rm_graph

    @rm_graph.setter
    def rm_graph(self, rm_graph: Graph) -> None:
        self.__path = rm_graph

    @property
    def graphs_set(self) -> list:
        """Method to get all input models as a list of graph objects

        :return: graphs_set
        :rtype: list
        """
        return self.__graphs_set

    @graphs_set.setter
    def graphs_set(self, graphs_set: list) -> None:
        self.__path = graphs_set

    @property
    def common_nodes(self) -> list:
        """Method to get the common nodes of all input models

        :return: common_nodes
        :rtype: list
        """
        return self.__common_nodes

    @common_nodes.setter
    def common_nodes(self, common_nodes: list) -> None:
        self.__common_nodes = common_nodes

    @property
    def rm_clusters(self) -> pd.DataFrame:
        """Method to get the clusters for the rm graph

        :return: rm_clusters
        :rtype: pd.DataFrame
        """

        return self.__rm_clusters

    @property
    def rm_graph_nodes(self) -> list:
        """Method to get the nodes which should be in the reference graph

        :return: rm_graph_nodes
        :rtype: list
        """
        return self.__rm_graph_nodes

    def create_initial_rm_graph(self) -> None:
        """Method to merge all input models into one model

        :return: None
        """
        self.__mcc_algorithm.load_graphs()
        self.__mcc_algorithm.initiate_sets()
        self.__mcc_algorithm.execute()

        # set the merged model as the initial graph
        initial_graph = self.__mcc_algorithm.rm_graph

        # delete the root nodes and edges out of the 'initial_graph'
        root_node_id = 'NoneNone'
        initial_graph.delete_node(root_node_id)
        initial_graph.delete_root_edges()

        # set the graphs set and the initial rm_graph
        self.__rm_graph = initial_graph
        self.__graphs_set = self.__mcc_algorithm.graphs

    def compute_common_nodes(self) -> None:
        """Method to compute the common nodes out of the nodes of all input models

        :return: None
        """
        self.__common_nodes = compute_common_nodes(self.__mcc_algorithm.nodes_set)

    def build_nodes_clusters(self) -> None:
        """Method to compute groups of nodes for all input models

        :return: None
        """
        compute_clusters_for_all_input_graphs(self.graphs_set)

    def evaluate_nodes_clusters(self) -> None:
        """Method to compute the best group for every cluster over all input models

        :return: None
        """
        # get the best group for every cluster over all input models
        self.__rm_clusters = evaluate_clusters(self.graphs_set)

    def compute_rm_graph_nodes(self) -> None:
        """Method to compute the nodes which should be marked as reference

        :return: None
        """
        # compute the updated node_ids for all nodes in 'rm_clusters'
        self.__rm_graph_nodes = compute_rm_graph_nodes(self.common_nodes, self.rm_clusters)

    def create_final_rm_graph(self) -> None:
        """Method to build the finale rm_graph

        :return: None
        """
        # compute the final reference graph
        create_final_rm_graph(self.rm_graph_nodes, self.rm_graph)

from mcc.mcc_views import *
from refpa.utils_refpa import compute_common_nodes, compute_clusters_for_all_input_graphs, evaluate_clusters, \
    compute_rm_graph_nodes, create_final_rm_graph


class RefPaViews:

    def __init__(self, path: str) -> None:
        """Constructor

        :param str path: relative path to directory where the xml files for the input models are located
        """
        self.__path = path
        self.__rm_graphs = pd.DataFrame(columns=['rm_graph'])
        self.__initial_graphs_views = pd.DataFrame(columns=['initial_rm_graph', 'input_views', 'common_nodes'])

    @property
    def path(self):
        """Method to get the path where the files for the input models are located

        :return: path
        :rtype: str
        """
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        self.__path = str(path)

    @property
    def rm_graphs(self) -> pd.DataFrame:
        """Method to get the set of final reference graphs

        :return: rm_graphs
        :rtype: pd.DataFrame
        """
        return self.__rm_graphs

    @rm_graphs.setter
    def rm_graphs(self, rm_graphs: pd.DataFrame) -> None:
        self.__rm_graphs = rm_graphs

    def create_initial_rm_graphs(self) -> None:
        """Method to merge the viewpoints of all input models into one model per viewpoint
        and to compute the common nodes of for the viewpoints of all input models

        :return: None
        """
        # set the path to the directory where the xml files for the input models are located
        path = self.path

        # set the parameters of the mcc_views_algorithm
        mcc_move_cost = float(2.0)
        mcc_delete_cost = float(1.0)
        mcc_insert_cost = float(10.0)
        mcc_threshold = -100.0
        # execute mcc_views_algorithm to merge viewpoints of all input models into one model per viewpoint
        mcc_views_algorithm = MCCViews(path, mcc_move_cost, mcc_delete_cost, mcc_insert_cost, mcc_threshold)
        mcc_views_algorithm.load_graphs_views()

        models = mcc_views_algorithm.graphs
        view_names = mcc_views_algorithm.view_names
        number_of_views = len(view_names)
        """Iterate over all different viewpoints of all input models to initialize the common nodes 
        and the initial_rm_graph for every viewpoint.
        """
        for i in range(0, number_of_views):
            current_views = []
            # get the name of the current_view
            current_view_name = view_names[i]
            print(current_view_name)
            # iterate over all models
            for j in range(0, len(models)):
                # check if current model contains current view
                try:
                    # get the current view of the current model
                    current_model_view = models.iloc[j]['model'].loc[current_view_name].loc['graph']
                    # append current view to 'current_views'
                    current_views.append(current_model_view)
                except KeyError as ke:
                    input_graph_name = models.iloc[j].name
                    print(
                        'Viewpoint \'' + current_view_name + '\' does not exist for input graph \'' + input_graph_name + '\'!')
                    continue

            # initiate edges and nodes set of 'mcc_views_algorithm' for 'current_views'
            mcc_views_algorithm.current_views = current_views
            mcc_views_algorithm.initiate_sets()

            # execute 'mcc_views_algorithm' on 'current_views' to merge views of all input models into one model
            mcc_views_algorithm.execute()

            # create deep copy of result model of 'mcc_views_algorithm'
            initial_rm_graph = copy.deepcopy(mcc_views_algorithm.rm_graph)

            # delete root nodes and root edges out of 'initial_rm_graph'
            root_node_id = 'NoneNone'
            initial_rm_graph.delete_node(root_node_id)
            initial_rm_graph.delete_root_edges()

            # compute common nodes for viewpoints of all input models
            common_nodes = compute_common_nodes(mcc_views_algorithm.nodes_set)

            # add 'initial_rm_graph' and 'common_nodes' for the current viewpoint to 'initial_graphs_views'
            self.__initial_graphs_views.loc[current_view_name] = [initial_rm_graph, current_views, common_nodes]

    def execute(self) -> None:
        """Method to execute the RefPa-views algorithm on the single views of the input models

        :return: None
        """

        for i in range(0, len(self.__initial_graphs_views)):
            # get current viewpoints
            current_input_views = self.__initial_graphs_views.iloc[i]['input_views']
            # compute the clusters (groups of nodes) for all input models
            compute_clusters_for_all_input_graphs(current_input_views)
            # get the best group for every cluster over all viewpoint models
            current_view_rm_clusters = evaluate_clusters(current_input_views)
            current_input_views_common_nodes = self.__initial_graphs_views.iloc[i]['common_nodes']
            # compute the updated node_ids for all nodes in 'rm_clusters'
            current_rm_graph_nodes = compute_rm_graph_nodes(current_input_views_common_nodes, current_view_rm_clusters)
            # compute the final reference graph for the current viewpoints
            current_initial_rm_graph = self.__initial_graphs_views.iloc[i]['initial_rm_graph']
            create_final_rm_graph(current_rm_graph_nodes, current_initial_rm_graph)

            # get the name of current viewpoints
            current_rm_graph_name = self.__initial_graphs_views.iloc[i].name
            # add final reference graph for current viewpoints to 'rm_graphs'
            self.__rm_graphs.loc[current_rm_graph_name] = current_initial_rm_graph

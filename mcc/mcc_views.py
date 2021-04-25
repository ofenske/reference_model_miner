import copy

from core.loader.data_loader import *
from core.model.edges_set import *
from core.model.graph import *
from core.model.nodes_set import *
from core.model.reserved_edges_set import *
from mcc.utils_mcc import update_nodes_set, update_edges_set, initialize_cost_values, \
    compute_artificial_edges, check_graph_for_all_reserved_edges, check_graph_for_relevant_reserved_edges


class MCCViews:

    def __init__(self, path: str, move_cost: float, delete_cost: float, insert_cost: float, threshold: float) -> None:
        """Constructor

        :param str path: The path to the directory where your files are located
        :param float move_cost: The cost for the move operation
        :param float delete_cost: The cost for the delete operation
        :param float insert_cost: The cost for the insert operation
        :param: float threshold: The threshold the edges have to fulfill to get into the reference graph
        """
        self.__path = r'' + path
        self.__graphs = pd.DataFrame(columns=['model'])
        self.__edges_set = EdgesSet()
        self.__nodes_set = NodesSet()
        self.__reserved_edges_set = ReservedEdgesSet()
        self.__move_cost = float(move_cost)
        self.__delete_cost = float(delete_cost)
        self.__insert_cost = float(insert_cost)
        self.__threshold = float(threshold)
        self.__rm_graph = None
        self.__current_views = []
        self.__view_names = []

    @property
    def path(self) -> str:
        """Method to get the path

        :return: path
        :rtype: str
        """
        return self.__path

    @path.setter
    def path(self, path: str) -> None:
        self.__path = path

    @property
    def graphs(self) -> list:
        """Method to get all graphs

        :return: graphs
        :rtype: list
        """
        return self.__graphs

    @graphs.setter
    def graphs(self, graphs: list) -> None:
        self.__graphs = graphs

    @property
    def edges_set(self) -> pd.DataFrame:
        """Method to get all edges of edges_set

        :return: edges_set
        :rtype: pd.DataFrame
        """
        return self.__edges_set.edges_set

    @edges_set.setter
    def edges_set(self, edges_set: pd.DataFrame) -> None:
        self.__edges_set = edges_set

    @property
    def nodes_set(self) -> pd.DataFrame:
        """Method to get all nodes of nodes_set

        :return: nodes_set
        :rtype: pd.DataFrame
        """
        return self.__nodes_set.nodes_set

    @nodes_set.setter
    def nodes_set(self, nodes_set: pd.DataFrame):
        self.__nodes_set = nodes_set

    @property
    def move_cost(self) -> float:
        """Method to get the move_cost

        :return: move_cost
        :rtype: float
        """
        return self.__move_cost

    @move_cost.setter
    def move_cost(self, move_cost: float):
        self.__move_cost = float(move_cost)

    @property
    def delete_cost(self) -> float:
        """Method to get the delete_cost

        :return: delete_cost
        :rtype: float
        """
        return self.__delete_cost

    @delete_cost.setter
    def delete_cost(self, delete_cost: float):
        self.__delete_cost = float(delete_cost)

    @property
    def insert_cost(self) -> float:
        """Method to get the insert_cost

        :return:insert_cost
        :rtype: float
        """
        return self.__insert_cost

    @insert_cost.setter
    def insert_cost(self, insert_cost: float):
        self.__insert_cost = float(insert_cost)

    @property
    def threshold(self) -> float:
        """Method to get the threshold

        :return: threshold
        :rtype: float
        """
        return self.__threshold

    @threshold.setter
    def threshold(self, threshold: float):
        self.__threshold = float(threshold)

    @property
    def rm_graph(self) -> Graph:
        """Method to get the reference model graph

        :return: rm_graph
        :rtype: Graph
        """
        return self.__rm_graph

    @property
    def current_views(self) -> list:
        """Method to get the current views to operate on

        :return: current_views
        :rtype: list
        """
        return self.__current_views

    @current_views.setter
    def current_views(self, current_views: list) -> None:

        self.__current_views = current_views

    @property
    def view_names(self) -> list:
        return self.__view_names

    def get_most_frequent_edge(self) -> pd.Series:
        """Method to get the most frequent_edges out of edges_set

        :return: most_frequent_edge
        :rtype: pd.Series
        """
        return self.__edges_set.get_most_frequent_edge()

    def add_graph(self, graph: Graph) -> None:
        """Method to add a graph to graphs

        :param graph: The graph to add
        :return: None
        """
        self.__graphs.append(graph)

    def load_graphs_views(self):
        """Method to load xml documents from the specified directory and transform them into a set of graphs

        """
        data_loader = DataLoader(self.__path)
        # get filenames of all files in specified directory
        filenames = data_loader.load_file_names()

        # open all files and convert them into graphs
        for filename in filenames:
            # load the current file into a dict
            doc = data_loader.load_file(self.__path + '\\' + str(filename))
            # initialize the DataFrame for the doc views
            doc_views = pd.DataFrame(columns=['nodes', 'edges'])
            # get all views of 'doc'
            views = data_loader.get_all_views(doc)

            # iterate over all views to get the node and edge ids of all views
            for i in range(0, len(views)):
                view_name = str(views[i]['name']['#text']).lower()
                view_nodes = data_loader.get_view_nodes(views[i])
                if len(view_nodes) is 0:
                    continue
                # view_id = data_loader.get_view_name(view_name)
                view_edges = data_loader.get_view_edges(views[i])
                doc_views.loc[view_name] = [view_nodes, view_edges]
                if view_name not in self.__view_names:
                    self.__view_names.append(view_name)

            # initialize the final DataFrame for the views of the graph
            graph_views = pd.DataFrame(columns=['nodes', 'edges'])
            # iterate over all views in 'doc_views' to get the edge and node objects out of 'doc'
            for i in range(0, len(doc_views)):
                current_view = doc_views.iloc[i]
                current_view_name = current_view.name
                current_view_nodes = data_loader.get_all_view_nodes_objects(doc, current_view.loc['nodes'])
                current_view_edges = data_loader.get_all_view_edges_objects(doc, current_view.loc['edges'],
                                                                            current_view.loc['nodes'])
                graph_views.loc[current_view_name] = [current_view_nodes, current_view_edges]

            model_graphs = pd.DataFrame(columns=['graph'])

            # iterate over all views in 'graph_views'
            for i in range(0, len(graph_views)):
                current_graph_nodes = graph_views.iloc[i]['nodes']
                current_graph_edges = graph_views.iloc[i]['edges']
                current_graph = Graph(current_graph_nodes, current_graph_edges)

                # initialize/compute the distinct nodes and edges of 'graph'
                current_graph.initialize_distinct_nodes()
                current_graph.initialize_distinct_edges()

                model_graphs.loc[graph_views.iloc[i].name] = [current_graph]

            self.__graphs.loc[filename] = [model_graphs]

    def initiate_sets(self):
        """Method to initiate edges_set and nodes_set for the MCC algorithm

        """

        # get the size of 'current_views'
        current_views_size = len(self.__current_views)
        self.nodes_set.drop(self.nodes_set.index, inplace=True)
        self.edges_set.drop(self.edges_set.index, inplace=True)
        self.__reserved_edges_set.reserved_edges_set.drop(self.__reserved_edges_set.reserved_edges_set.index,
                                                          inplace=True)

        # insert all edges and nodes of 'view' into 'edges_set' and 'nodes_set'
        for view in self.current_views:
            update_nodes_set(view, self.__nodes_set)
            update_edges_set(view, self.__edges_set)

        # create artificial edge for all root_nodes
        compute_artificial_edges(self.nodes_set, self.edges_set)

        # all nodes and edges are inserted --> create relativ frequency's
        self.nodes_set['frequency'] = self.nodes_set['frequency'].apply(lambda x: x / current_views_size)
        self.edges_set['frequency'] = self.edges_set['frequency'].apply(lambda x: x / current_views_size)

        # initialize cost_value for all edges
        initialize_cost_values(self.__edges_set, self.__nodes_set, self.move_cost, self.insert_cost,
                               self.delete_cost)

    def execute(self) -> None:
        """Method to execute the MCC-views algorithm

        :return:
        """
        # flag if frequent_edge_exists
        frequent_edge_exists = True

        # nodes and edges to build the initial rm_graph
        rm_edges = pd.DataFrame(columns=['source', 'target', 'type','frequency'])
        rm_nodes = pd.DataFrame.from_dict({'NoneNone': [None, None, None]}, orient='index', columns=['label', 'type','frequency'])

        # build initial rm_graph
        self.__rm_graph = Graph(rm_nodes, rm_edges)

        # add new edges until 'frequent_edge_exists' is False
        while frequent_edge_exists is True:
            # get the most frequent edge out of edges_set
            new_edge = copy.deepcopy(self.__edges_set.get_most_frequent_edge())

            # check if 'new_edge' is None (this is the case when we already get all edges out of 'edges_set'
            # -> 'edges_set' is then empty)
            if new_edge is None:
                frequent_edge_exists = False

                # check for all edges in 'reserved_edges_set' if we can add them to rm_graph
                check_graph_for_all_reserved_edges(self.__reserved_edges_set, self.__rm_graph)

            # get all the attributes we need for the 'new_edge'
            else:
                new_edge_cost_value = new_edge.loc['cost_value']
                new_edge_frequency = new_edge.loc['frequency']
                new_edge_target_node_id = str(new_edge.loc['target'].name)
                new_edge_source_node_id = str(new_edge.loc['source'].name)

                # delete 'new_edge' from 'edges_set'
                self.__edges_set.delete_edge(str(new_edge.name))

            # check if 'new_edge_frequency' is above 'threshold' and if 'frequent_edge_exists' is True
            if new_edge_cost_value >= self.threshold and frequent_edge_exists is True:
                # update the cost_value of all edges in 'edges_set'
                self.__edges_set.update_cost_value(new_edge_target_node_id, self.move_cost)

                # check if the source node of "new_edge' already exists in 'rm_graph'
                source_node_exists = self.__rm_graph.node_exists(new_edge_source_node_id)

                # if source node is already in 'rm_graph' execute the block
                if source_node_exists is True:
                    # add the 'new_edge' and the new node (target node of 'new_edge') to 'rm_graph'
                    self.__rm_graph.add_edge(new_edge)
                    new_edge_target_node = new_edge.loc['target']
                    frequency = self.get_node_frequency(new_edge_target_node)
                    self.__rm_graph.add_node(new_edge_target_node, frequency)

                    # check if we can add edges of 'reserved_edges_set' to the new graph
                    # (this is the case if one these edges have 'new_edge_target_node' as their source_node
                    check_graph_for_relevant_reserved_edges(self.__reserved_edges_set, new_edge_target_node_id,
                                                            self.__rm_graph)

                # if 'new_edge_source_node' is not in rm_graph add 'new_edge' to 'reserved_new_edges'
                else:
                    self.__reserved_edges_set.add_edge(new_edge)

            else:
                frequent_edge_exists = False

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

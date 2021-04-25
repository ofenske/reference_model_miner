import codecs

from ream_miner.ream_miner import ReamMiner
from mcc.mcc_global import *
from mcc.mcc_views import *
from refpa.refpa_global import *
from refpa.refpa_views import *
import copy


def execute_mcc(input_path: str, output_path: str, threshold) -> None:
    """Method to execute the MCC algorithm on the global input models

    :return: None
    """
    # set the path to directory where all xml files of the input models are located
    path = input_path
    # set the costs for move, delete, insert operation and for the threshold
    move_cost = float(2.0)
    delete_cost = float(1.0)
    insert_cost = float(10.0)
    # initialize mcc algorithm
    mcc_algorithm = MCCGlobal(path, move_cost, delete_cost, insert_cost, threshold)

    # do first step of mcc algorithm: load all input models out of xml files into graph data structure
    mcc_algorithm.load_graphs()
    # do second step of mcc algorithm: compute the initial edges and nodes set over all input models
    mcc_algorithm.initiate_sets()
    # do third step of mcc algorithm: execute the algorithm
    mcc_algorithm.execute()

    # write nodes and edges set of the resulting reference graph to csv document
    # (first parameter = relative path to directory where one want to save the files)
    path = output_path + "\\" + 'nodes.csv'
    mcc_algorithm.rm_graph.nodes.to_csv(path, sep=",", index_label='id')
    path = output_path + "\\" + 'edges.csv'
    mcc_algorithm.rm_graph.edges.to_csv(path, sep=",", index_label='id')

    # get the node and edges stats
    node_stats = Nodes(mcc_algorithm.rm_graph.nodes).node_stats
    edge_stats = Edges(mcc_algorithm.rm_graph.edges).edge_stats
    if node_stats is not None:
        node_stats_path = output_path + '\\stats' + '\\' + 'node_stats.csv'
        node_stats.to_csv(node_stats_path, sep=",", index_label='type', header=['count'])
    if edge_stats is not None:
        edge_stats_path = output_path + '\\stats' + '\\' + 'edge_stats.csv'
        edge_stats.to_csv(edge_stats_path, sep=",", index_label='type', header=['count'])

    # create the root_element for the ArchiMate-Model
    root_element = mcc_algorithm.rm_graph.to_lxml_element()
    # update the root_element to get a ncname valid element
    root_element = Graph.recreate_identifier(root_element)
    # get the xml string
    xml = Graph.element_to_xml_string(root_element)
    # create the ArchiMate exchange file
    f = codecs.open(output_path + "/" + "reference_model.xml", "w+", "utf-8")
    f.write(xml)
    f.close()


def execute_mcc_views(input_path: str, output_path: str, threshold: float) -> None:
    """Method to execute the MCC-views algorithm on the single views of the input models

    :return: None
    """
    # set the path to directory where all xml files of the input models are located
    path = input_path
    # set the costs for move, delete, insert operation and for the threshold
    move_cost = float(2.0)
    delete_cost = float(1.0)
    insert_cost = float(10.0)
    # initialize mcc views algorithm (operates on the single views, not on the global model!!!!!!)
    mcc_views_algorithm = MCCViews(path, move_cost, delete_cost, insert_cost, threshold)

    # do first step of mcc algorithm: load all views of input models out of xml files into graph data structure
    mcc_views_algorithm.load_graphs_views()

    # initialize the DataFrame where one want to save all resulting reference graphs for the different views
    reference_graphs = pd.DataFrame(columns=['graph'])

    # get all views of all input models
    models = mcc_views_algorithm.graphs
    view_names = mcc_views_algorithm.view_names
    number_of_views = len(view_names)

    # iterate over all views
    for i in range(0, number_of_views):
        # local variable to save the set of views we currently work on
        current_views = []
        # get the name of the current_view
        current_view_name = view_names[i]
        # print output to see the progress of the algorithm
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
        # execute the mcc views algorithm for the current views as the set of input graphs
        mcc_views_algorithm.current_views = current_views

        # do second step of mcc algorithm: compute the initial edges and nodes set over all input models
        mcc_views_algorithm.initiate_sets()
        # do third step of mcc algorithm: execute the algorithm
        mcc_views_algorithm.execute()

        # create a deep copy 'rm_graph' attribute of mcc algorithm
        # this is because that attribute will e overwritten in the next iteration for the next viewpoints
        # else the results would be lost
        rm_graph = copy.deepcopy(mcc_views_algorithm.rm_graph)
        # save the copy in 'reference_graphs'
        reference_graphs.loc[current_view_name] = [rm_graph]

    """ After we executed the mcc algorithm for all viewpoints of all input models, all result reference graphs will 
    be saved in 'reference_graphs' -> iterate over all graphs in 'reference_graphs' to save their nodes and edges 
    in csv files"""
    # initiate the root_element (for the ArchiMate-Model)
    root_element = None
    for i in range(0, len(reference_graphs)):
        # get the name of the reference graph of the current viewpoint (= viewpoint name)
        current_rm_graph_name = reference_graphs.iloc[i].name
        # get the reference graph of the current viewpoint
        current_rm_graph = reference_graphs.iloc[i]['graph']

        # get all edges and nodes of 'current_rm_graph'
        current_rm_graph_edges = current_rm_graph.edges
        current_rm_graph_nodes = current_rm_graph.nodes

        # build the file name (= viewpoint name)
        file_name = str(current_rm_graph_name).replace('/', '_')
        # update the root_element with the current view name
        root_element = current_rm_graph.to_lxml_element(file_name, root_element)
        # set the path to place where you want to save the csv file for the nodes set of 'current_rm_graph'
        file_path = output_path + '\\' + file_name + '_nodes.csv'
        # save nodes to csv
        current_rm_graph_nodes.to_csv(file_path, sep=",", index_label='id')
        # set the path to place where you want to save the csv file for the edges set of 'current_rm_graph'
        file_path = output_path + '\\' + file_name + '_edges.csv'
        # save edges to csv
        current_rm_graph_edges.to_csv(file_path, sep=",", index_label='id')

        # get the node and edges stats
        node_stats = Nodes(current_rm_graph.nodes).node_stats
        edge_stats = Edges(current_rm_graph.edges).edge_stats
        if node_stats is not None:
            node_stats_path = output_path + '\\stats' + '\\' + file_name + '_node_stats.csv'
            node_stats.to_csv(node_stats_path, sep=",", index_label='type', header=['count'])
        if edge_stats is not None:
            edge_stats_path = output_path + '\\stats' + '\\' + file_name + '_edge_stats.csv'
            edge_stats.to_csv(edge_stats_path, sep=",", index_label='type', header=['count'])
    # update the root_element to get a ncname valid element
    root_element = Graph.recreate_identifier(root_element)
    # get the xml string
    xml = Graph.element_to_xml_string(root_element)
    # create the ArchiMate exchange file
    f = codecs.open(output_path + "/" + "reference_model.xml", "w+", "utf-8")
    f.write(xml)
    f.close()


def execute_refpa(input_path: str, output_path: str):
    """Method to execute the RefPa algorithm on the global input models

    :return:
    """
    # initialize refpa algorithm
    refpa_algorithm = RefPaGlobal(input_path)

    # Step one of refpa algorithm: merge all input models into one global input model
    refpa_algorithm.create_initial_rm_graph()
    # Step two of refpa algorithm: compute the common-practice nodes
    refpa_algorithm.compute_common_nodes()
    # Step three of refpa algorithm: build nodes clusters
    refpa_algorithm.build_nodes_clusters()
    # Step four of refpa algorithm: evaluate nodes clusters to get the best group for every cluster
    refpa_algorithm.evaluate_nodes_clusters()
    # Step five of refpa algorithm: compute all nodes which should be in the final reference graph
    refpa_algorithm.compute_rm_graph_nodes()
    # Step six of refpa algorithm: build the final reference graph
    refpa_algorithm.create_final_rm_graph()

    # write nodes and edges set of the resulting reference graph to csv document
    # (first parameter = relative path to directory where one want to save the files)
    path = output_path + "\\" + "nodes.csv"
    refpa_algorithm.rm_graph.nodes.to_csv(path, sep=",", index_label='id')
    path = output_path + "\\" + "edges.csv"
    refpa_algorithm.rm_graph.edges.to_csv(path, sep=",", index_label='id')

    # get the node and edges stats
    node_stats = Nodes(refpa_algorithm.rm_graph.nodes).node_stats
    edge_stats = Edges(refpa_algorithm.rm_graph.edges).edge_stats
    if node_stats is not None:
        node_stats_path = output_path + '\\stats' + '\\' + 'node_stats.csv'
        node_stats.to_csv(node_stats_path, sep=",", index_label='type', header=['count'])
    if edge_stats is not None:
        edge_stats_path = output_path + '\\stats' + '\\' + 'edge_stats.csv'
        edge_stats.to_csv(edge_stats_path, sep=",", index_label='type', header=['count'])

    # create the root_element for the ArchiMate-Model
    root_element = refpa_algorithm.rm_graph.to_lxml_element()
    # update the root_element to get a ncname valid element
    root_element = recreate_identifier(root_element)
    # get the xml string
    xml = element_to_xml_string(root_element)
    # create the ArchiMate exchange file
    f = codecs.open(output_path + "/" + "reference_model.xml", "w+", "utf-8")
    f.write(xml)
    f.close()


def execute_refpa_views(input_path: str, output_path: str):
    """Method to execute the RefPa-views algorithm on the single views of the input models

    :return:
    """
    # initialize refpa algorithm
    refpa_views_algorithm = RefPaViews(input_path)

    # do first step of refpa algorithm: merge the different views of input models into global input models
    refpa_views_algorithm.create_initial_rm_graphs()
    # do second step of refpa algorithm: compute common nodes, compute nodes groups, evaluate nodes groups,
    # create final reference graph for a the different viewpoints
    refpa_views_algorithm.execute()

    # get the different reference graphs for the different viewpoints
    final_rm_graphs = refpa_views_algorithm.rm_graphs

    # initiate the root_element (for the ArchiMate-Model)
    root_element = None
    # iterate over all reference graph in 'final_rm_graphs' to write their nodes and edges to csv files
    for i in range(0, len(final_rm_graphs)):
        # get the name of the reference graph of the current viewpoint (= viewpoint name)
        current_rm_graph_name = final_rm_graphs.iloc[i].name

        # get all edges and nodes of 'current_rm_graph'
        current_rm_graph = final_rm_graphs.iloc[i]['rm_graph']
        current_rm_graph_edges = current_rm_graph.edges
        current_rm_graph_nodes = current_rm_graph.nodes
        # build the file name (= viewpoint name)
        file_name = str(current_rm_graph_name).replace('/', '_')
        # update the root_element with the current view name
        root_element = current_rm_graph.to_lxml_element(file_name, root_element)
        # set the path to place where you want to save the csv file for the nodes set of 'current_rm_graph'
        file_path = output_path + '\\' + file_name + '_nodes.csv'
        # save nodes to csv
        current_rm_graph_nodes.to_csv(file_path, sep=",", index_label='id')
        # set the path to place where you want to save the csv file for the edges set of 'current_rm_graph'
        file_path = output_path + '\\' + file_name + '_edges.csv'
        # save edges to csv
        current_rm_graph_edges.to_csv(file_path, sep=",", index_label='id')

        # get the node and edges stats
        node_stats = Nodes(current_rm_graph.nodes).node_stats
        edge_stats = Edges(current_rm_graph.edges).edge_stats
        if node_stats is not None:
            node_stats_path = output_path + '\\stats' + '\\' + file_name + '_node_stats.csv'
            node_stats.to_csv(node_stats_path, sep=",", index_label='type', header=['count'])
        if edge_stats is not None:
            edge_stats_path = output_path + '\\stats' + '\\' + file_name + '_edge_stats.csv'
            edge_stats.to_csv(edge_stats_path, sep=",", index_label='type', header=['count'])

    # current_rm_graph_edges.to_csv(file_path, sep=",", index_label='id')
    # update the root_element to get a ncname valid element
    root_element = Graph.recreate_identifier(root_element)
    # get the xml string
    xml = Graph.element_to_xml_string(root_element)
    # create the ArchiMate exchange file
    f = codecs.open(output_path + "/" + "reference_model.xml", "w+", "utf-8")
    f.write(xml)
    f.close()


def execute_combined_views(input_path: str, output_path: str, threshold: float):
    """Method to execute the RefPa-views algorithm on the single views of the input models

    :return:
    """
    # initialize refpa algorithm
    ream_miner = ReamMiner(input_path, threshold)

    # do first step of refpa algorithm: merge the different views of input models into global input models
    ream_miner.create_initial_rm_graphs()
    # do second step of refpa algorithm: compute common nodes, compute nodes groups, evaluate nodes groups,
    # create final reference graph for a the different viewpoints
    ream_miner.execute()

    # get the different reference graphs for the different viewpoints
    final_rm_graphs = ream_miner.rm_graphs

    # initiate the root_element (for the ArchiMate-Model)
    root_element = None
    # iterate over all reference graph in 'final_rm_graphs' to write their nodes and edges to csv files
    for i in range(0, len(final_rm_graphs)):
        # get the name of the reference graph of the current viewpoint (= viewpoint name)
        current_rm_graph_name = final_rm_graphs.iloc[i].name

        # get all edges and nodes of 'current_rm_graph'
        current_rm_graph = final_rm_graphs.iloc[i]['rm_graph']
        current_rm_graph_edges = current_rm_graph.edges
        current_rm_graph_nodes = current_rm_graph.nodes
        # build the file name (= viewpoint name)
        file_name = str(current_rm_graph_name).replace('/', '_')
        # update the root_element with the current view name
        root_element = current_rm_graph.to_lxml_element(file_name, root_element)
        # set the path to place where you want to save the csv file for the nodes set of 'current_rm_graph'
        file_path = output_path + '\\' + file_name + '_nodes.csv'
        # save nodes to csv
        current_rm_graph_nodes.to_csv(file_path, sep=",", index_label='id')
        # set the path to place where you want to save the csv file for the edges set of 'current_rm_graph'
        file_path = output_path + '\\' + file_name + '_edges.csv'
        # save edges to csv
        current_rm_graph_edges.to_csv(file_path, sep=",", index_label='id')

        # get the node and edges stats
        node_stats = Nodes(current_rm_graph.nodes).node_stats
        edge_stats = Edges(current_rm_graph.edges).edge_stats
        if node_stats is not None:
            node_stats_path = output_path + '\\stats' + '\\' + file_name + '_node_stats.csv'
            node_stats.to_csv(node_stats_path, sep=",", index_label='type', header=['count'])
        if edge_stats is not None:
            edge_stats_path = output_path + '\\stats' + '\\' + file_name + '_edge_stats.csv'
            edge_stats.to_csv(edge_stats_path, sep=",", index_label='type', header=['count'])
    # current_rm_graph_edges.to_csv(file_path, sep=",", index_label='id')
    # update the root_element to get a ncname valid element
    root_element = Graph.recreate_identifier(root_element)
    # get the xml string
    xml = Graph.element_to_xml_string(root_element)
    # create the ArchiMate exchange file
    f = codecs.open(output_path + "/" + "reference_model.xml", "w+", "utf-8")
    f.write(xml)
    f.close()


if __name__ == '__main__':
    """Main method for run file. Here you have to uncomment the algorithm you want to execute.
    """
    # AML
    execute_mcc(r'data/input_data/AML', r'data/results/mcc_global/AML', 4.0)
    execute_mcc_views(r'data/input_data/AML', r'data/results/mcc_views/AML', 4.0)
    execute_refpa(r'data/input_data/AML', r'data/results/refpa_global/AML')
    execute_refpa_views(r'data/input_data/AML', r'data/results/refpa_views/AML')
    execute_combined_views(r'data/input_data/AML', r'data/results/combined_views/AML', 4.0)

    # KYC
    execute_mcc(r'data/input_data/KYC', r'data/results/mcc_global/KYC', 4.0)
    execute_mcc_views(r'data/input_data/KYC', r'data/results/mcc_views/KYC', 4.0)
    execute_refpa(r'data/input_data/KYC', r'data/results/refpa_global/KYC')
    execute_refpa_views(r'data/input_data/KYC', r'data/results/refpa_views/KYC')
    execute_combined_views(r'data/input_data/KYC', r'data/results/combined_views/KYC', 4.0)

    # SSH
    execute_mcc(r'data/input_data/SSH', r'data/results/mcc_global/SSH', 4.0)
    execute_mcc_views(r'data/input_data/SSH', r'data/results/mcc_views/SSH', 4.0)
    execute_refpa(r'data/input_data/SSH', r'data/results/refpa_global/SSH')
    execute_refpa_views(r'data/input_data/SSH', r'data/results/refpa_views/SSH')
    execute_combined_views(r'data/input_data/SSH', r'data/results/combined_views/SSH', 4.0)

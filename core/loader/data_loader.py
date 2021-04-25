import os
import xmltodict
import pandas as pd
import collections
import copy


class DataLoader:

    def __init__(self, path: str = ''):
        self.__path = path

    def load_file_names(self, path: str = '') -> list:
        """Method to get all names of the files in a special directory.

        :param path: The path to the directory which contains all files one want to load
        :return: A list with the names of all files in it
        :rtype: list
        """
        if len(path) == 0:
            list_of_files = os.listdir(self.__path)
        else:
            list_of_files = os.listdir(path)

        return list_of_files

    @staticmethod
    def load_file(doc_path: str) -> dict:
        """Method to load one specific file

        :param doc_path: The path to the file one want to load
        :return: An ordered dictionary with all xml elements in it
        :rtype: dict
        """
        # open the file
        with open(doc_path, encoding='utf-8') as file:
            # convert xml document into dict
            doc = xmltodict.parse(file.read(), encoding='utf-8')

        return doc

    @staticmethod
    def get_all_nodes(doc: dict) -> pd.DataFrame:
        """Method to extract all nodes out of an xml/ArchiMate file.

        :param doc: The dictionary which contains all xml elements for a document/ArchiMate model
        :return: A DataFrame which contains all nodes of the ArchiMate model (with type and name as attributes)
        :rtype: pd.DataFrame
        """
        # get all nodes out of the xml document (list of dicts)
        xml_nodes = doc['model']['elements']['element']

        nodes = pd.DataFrame(columns=['label', 'type'])

        for node in xml_nodes:
            # get the id, type and name of 'node' (type(node) = dict)
            node_id = node['@identifier']
            node_type = node['@xsi:type']
            node_label = node['name']['#text']

            # append 'node' to 'nodes'
            nodes.loc[node_id] = [node_label, node_type]

        return nodes

    @staticmethod
    def get_all_edges(doc: dict) -> pd.DataFrame:
        """Method to extract all edges out of an xml/ArchiMate file.

        :param doc: The dictionary which contains all xml elements for a document/ArchiMate model
        :return: A DataFrame which contains all edges of the ArchiMate model (with source, target and type as attributes)
        :rtype: pd.DataFrame
        """
        # get all edges out of the xml document (list of dicts)
        xml_edges = doc['model']['relationships']['relationship']

        edges = pd.DataFrame(columns=['source', 'target', 'type'])

        for edge in xml_edges:
            # get the id, type and name of 'edge' (type(edge) = dict)
            edge_id = edge['@identifier']
            edge_source = edge['@source']
            edge_target = edge['@target']
            edge_type = edge['@xsi:type']

            # append 'edge' to 'edges'
            edges.loc[edge_id] = [edge_source, edge_target, edge_type]

        return edges

    def get_view_nodes(self, view: collections.OrderedDict) -> dict:
        """Method to get global ids of all nodes of a viewpoint out of xml document
        (and the ids of their encapsulated nodes)

        :param collections.OrderedDict view: The view with all its attributes
        :return: view_nodes as key:value (key = global id of node, value = list of the ids of the encapsulated nodes)
        :rtype: dict
        """
        # dic of nodes with their '@elementRef' tag as key and their child nodes as value
        # (every is represented by its '@elementRef tag, also the child nodes)
        view_nodes = {}
        try:
            # get all nodes objects of the view
            view_nodes_objects = view['node']
        except KeyError:
            return view_nodes
        # if there is only one node in 'view', the type of 'view_nodes_objects' will be collections.OrderedDict
        if type(view_nodes_objects) is collections.OrderedDict:
            # list of nodes (objects) which have not been handled so far
            unhandled_nodes = [view_nodes_objects]
        # # if there are multiple nodes in 'view', the type of 'view_nodes_objects' will be list
        else:
            # list of nodes (objects) which have not been handled so far
            unhandled_nodes = view_nodes_objects

        # execute block as long as there are nodes in 'unhandled_nodes'
        while len(unhandled_nodes) > 0:
            # get the first Node out of 'unhandled_nodes'
            current_node_object = unhandled_nodes.pop(0)

            if current_node_object['@xsi:type'] == 'Label':
                # if the type of 'current_node_object' is Label, then it will be skipped (we ignore label nodes)
                continue
            elif current_node_object['@xsi:type'] == 'Container':
                # if the type of 'current_node_object' is Container, then we want the children (encapsulated nodes)
                # 'current_node_object' itself (the container node) will be ignored
                container_children = self.__get_children(current_node_object)
                # append the 'container_children' (list of node objects) to 'unhandled_nodes'
                unhandled_nodes += container_children
            else:
                # get the id of 'current_node_object'
                current_node_id = copy.copy(current_node_object['@elementRef'])
                # get the children of 'current_node_object' (result = list of node objects)
                current_node_children = self.__get_children(current_node_object)
                # get the ids of all elements in 'current_node_children' (result = list of ids (strings))
                current_node_children_ids = self.__get_node_ids(current_node_children)
                # append 'current_node_children' to 'unhandled_nodes'
                unhandled_nodes += current_node_children
                # safe the current node with its id as key and its children as value in 'view_nodes'
                view_nodes[current_node_id] = current_node_children_ids
        return view_nodes

    @staticmethod
    def get_all_views(doc: dict) -> list:
        """ Method to get all views of an input model out of xml file

        :param dict doc: The dict object of the xml file of the current input model
        :return: graph_views
        :rtype: list
        """
        graph_views = doc['model']['views']['diagrams']['view']

        return graph_views

    @staticmethod
    def get_view_edges(view: collections.OrderedDict) -> list:
        """Method to get unique ids of all edges of a viewpoint out of xml document

        :param collections.OrderedDict view: The view with all its attributes
        :return: view_edges_ids
        :rtype: list
        """

        try:
            # get all edges of the viewpoint out of 'view'
            view_edges = view['connection']
            # special case if the view only has one edge (then the type of 'view_edges' is not list, but OrderedDict)
            if type(view_edges) == collections.OrderedDict:
                # get the edge id of the edge
                current_edge_id = view_edges['@relationshipRef']
                return [current_edge_id]
            # will be executed if we have more then one edge in the viewpoint
            else:
                # initialize a list for all edge ids
                view_edges_ids = []

                # iterate over all edges of the viewpoint
                for edge in view_edges:
                    # get the edge_id of the current edge
                    current_edge_id = edge['@relationshipRef']
                    # append the current edge to 'view_edges_ids'
                    view_edges_ids.append(current_edge_id)

                return view_edges_ids
        except KeyError:
            return []

    @staticmethod
    def get_all_view_nodes_objects(doc: dict, view_nodes: dict) -> pd.DataFrame:
        """Method to get all nodes of a viewpoint out of xml document

        :param dict doc: The dict object of the xml file of the current input model
        :param list nodes_ids: List of all node ids which are part of the viewpoint
        :return: nodes
        :rtype: pd.DataFrame
        """
        # initialize the DataFrame for the nodes
        nodes = pd.DataFrame(columns=['label', 'type'])

        nodes_ids = list(view_nodes.keys())
        # get all nodes of the complete input model
        model_nodes = doc['model']['elements']['element']

        # iterate over all nodes in 'model_nodes'
        for i in range(0, len(model_nodes)):
            # get the node id of the current node
            node_id = model_nodes[i]['@identifier']

            # check if the node id of the current node is in the list of node ids of the viewpoint ('nodes_ids')
            if node_id in nodes_ids:
                # get label and type of the current node
                node_label = model_nodes[i]['name']['#text']
                node_type = model_nodes[i]['@xsi:type']

                # append the current node to 'nodes'
                nodes.loc[node_id] = [node_label, node_type]

        return nodes

    @staticmethod
    def get_all_view_edges_objects(doc: dict, edges_ids: list, view_nodes: dict) -> pd.DataFrame:
        """Method to get all edges of a viewpoint out of xml document

        :param dict doc: The dict object of the xml file of the current input model
        :param dict view_nodes: Set of all nodes which are part of the viewpoint
        :param list edges_ids: List of all edge ids which are part of the viewpoint
        :return: edges_objects
        :rtype: pd.DataFrame
        """
        # initialize the DataFrame for the edges_objects
        edges_objects = pd.DataFrame(columns=['source', 'target', 'type'])

        # get all edges_objects of the complete input model
        model_edges = doc['model']['relationships']['relationship']

        nodes_ids = list(view_nodes.keys())

        # iterate over all edges_objects in 'model_edges'
        for i in range(0, len(model_edges)):
            # get the node id of the current edge
            edge_id = model_edges[i]['@identifier']
            # get source and target node of the current edge
            edge_source = model_edges[i]['@source']
            edge_target = model_edges[i]['@target']
            # get the type of the current edge
            edge_type = model_edges[i]['@xsi:type']

            # check if 'edge_id' is in 'edges_ids'
            if edge_id in edges_ids:
                # add edge to 'edges_objects'
                edges_objects.loc[edge_id] = [edge_source, edge_target, edge_type]

            # check if 'nodes_ids' contains 'edge_source'
            elif edge_source in nodes_ids:
                # get children of the 'edge_source'
                source_node_children = view_nodes[edge_source]
                # check if 'source_node_children' contains 'edge_target'
                # this is the case if target node is nested in source node
                if edge_target in source_node_children:
                    # add edge to 'edges_objects'
                    edges_objects.loc[edge_id] = [edge_source, edge_target, edge_type]

            # check the reverse case form above
            # check if 'nodes_ids' contains 'edge_target'
            elif edge_target in nodes_ids:
                # get children of the 'edge_target'
                target_node_children = view_nodes[edge_target]
                # check if 'target_node_children' contains 'edge_source'
                # this is the case if source node is nested in target node
                if edge_source in target_node_children:
                    # add edge to 'edges_objects'
                    edges_objects.loc[edge_id] = [edge_source, edge_target, edge_type]

            else:
                # continue with the next edge
                continue

        return edges_objects

    @staticmethod
    def __get_node_object(nodes: list, node_id: str) -> list:
        """Method to get a single node of a viewpoint out of xml document

        :param list nodes: A list of all nodes of the input model
        :param str node_id: The unique id of the node we want to get
        :return: node
        :rtype: list
        """
        for i in range(0, len(nodes)):
            current_node_id = nodes[i]['@identifier']
            if current_node_id == node_id:
                node_label = nodes[i]['name']['#text']
                node_type = nodes[i]['@xsi:type']
                node = [node_label, node_type]

        return node

    @staticmethod
    def __get_children(node: collections.OrderedDict) -> list:
        """Method to get the children (encapsulated nodes) of a node.

        :param collections.OrderedDict node: The node for which one want to get the children
        :return: A list with all node objects of the children
        :rtype: list
        """
        # check if 'node' has child nodes
        try:
            children = node['node']
            # 'node' has only one child
            if type(children) is collections.OrderedDict:
                return [children]
            # 'node' has several children
            else:
                return children
        except KeyError:
            return []

    @staticmethod
    def __get_node_ids(nodes: list) -> list:
        """Method to get the node ids from a set of node objects

        :param str nodes: The set of node objects
        :return: A list with ids of all nodes
        :rtype: list
        """
        node_ids = []
        for node in nodes:
            try:
                node_id = copy.copy(node['@elementRef'])
                node_ids.append(node_id)
            # ignore all nodes which are from type 'label' or 'container'
            except KeyError:
                continue
        return node_ids

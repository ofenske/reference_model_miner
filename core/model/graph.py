from core.model.nodes import *
from core.model.edges import *
from core.model.nodes_set import NodesSet
from core.model.utils_nodes import node_exists
from core.model.utils_edges import edge_exists
from core.model.nodes_clusters import *
from core.model.utils_graph import *
import re

CHARACTERS = (
        string.ascii_letters
        + string.digits
        + '-._'
)
CHARACTER = (string.ascii_letters)


class Graph:

    def __init__(self, nodes: pd.DataFrame, edges: pd.DataFrame) -> None:
        """Constructor

        :param pd.DataFrame nodes: Contains all nodes of the graph. Should be in the following format: label|type
        :param pd.DataFrame edges: Contains all edges of the graph. Should be in the following format: source|target|type
        """
        self.__nodes = Nodes(nodes)
        self.__edges = Edges(edges)
        self.__nodes_clusters = NodesClusters()

    @property
    def nodes(self) -> pd.DataFrame:
        """All nodes (label, type)

        :return: nodes
        :rtype: pd.DataFrame
        """
        return self.__nodes.nodes

    @nodes.setter
    def nodes(self, nodes: pd.DataFrame) -> None:
        self.__nodes.nodes = nodes

    @property
    def distinct_nodes(self) -> pd.DataFrame:
        """Method to get all distinct nodes of a graph

        :return: distinct_nodes in the format index|label|type (index=label+type)
        :rtype: pd.DataFrame
        """
        return self.__nodes.distinct_nodes

    @property
    def nodes_clusters(self) -> pd.DataFrame:
        """Method to get the nodes clusters of a graph

        :return: nodes_clusters
        :rtype: pd.DataFrame
        """
        return self.__nodes_clusters.nodes_clusters

    @property
    def edges(self) -> pd.DataFrame:
        """All edges (source, target, type)

        :return: edges
        :rtype: pd.DataFrame
        """
        return self.__edges.edges

    @edges.setter
    def edges(self, edges: pd.DataFrame) -> None:
        self.__edges.edges = edges

    @property
    def distinct_edges(self) -> pd.DataFrame:
        """Method to get all distinct edges of a graph

        :return: distinct_edges in the format index|source|target|type (index=source+target+type)
        :rtype: pd.DataFrame
        """
        return self.__edges.distinct_edges

    def add_node(self, node: pd.Series, node_frequency) -> bool:
        """Method to add a new node to an existing graph

        :param node: The node to add to the existing graph
        :param node_frequency: The frequency of the current node
        """
        return self.__nodes.add_node(node, node_frequency)

    def initialize_distinct_nodes(self):
        """Method to initialize the distinct_nodes

        """
        self.__nodes.initialize_distinct_nodes(self.edges)

    def node_exists(self, node_id: str) -> bool:
        """Method to check if a specific nodes exists in the graph

        :param str node_id: The id of the node
        :return: True|False
        :rtype: bool
        """
        return node_exists(self.nodes, node_id)

    def delete_node(self, node_id: str) -> None:
        """Method to delete a node

        :param str node_id: The id of the node you want to delete
        """
        self.__nodes.delete_node(node_id)

    def compute_reference_nodes(self, rm_graph_nodes: list) -> None:
        """Method to mark all reference model nodes in the graph

        :param list rm_graph_nodes: The set of all nodes which should be included in the rm_graph
        """

        self.__nodes.compute_reference_nodes(rm_graph_nodes)

    def compute_nodes_clusters(self) -> None:
        """Method to compute the nodes clusters for the graph.

        :return:
        """
        self.__nodes_clusters.cluster_by_high_level_nodes(self.nodes, self.edges)
        # self.__nodes_clusters.compute_nodes_clusters(self.nodes)
        # self.__nodes_clusters.compute_cluster_connectivities(self.edges)
        # self.__nodes_clusters.update_node_ids(self.nodes)

    def add_edge(self, edge: pd.Series) -> bool:
        """Method to add a new node to an existing graph

        :param edge: The edge to add to the existing graph
        """
        return self.__edges.add_edge(edge)

    def edge_exists(self, edge_id: str) -> bool:
        """Method to check if a specific edge exists

        :param str edge_id: The id of the edge
        :return: True|False
        :rtype: bool
        """
        return edge_exists(self.edges, edge_id)

    def initialize_distinct_edges(self) -> None:
        """Method to initialize the distinct edges

        """
        self.__edges.initialize_distinct_edges(self.nodes, self.distinct_nodes)

    def delete_root_edges(self) -> None:
        """Method to delete all root edges of the graph
        """
        self.__edges.delete_root_edges()

    def delete_edge(self, edge_id: str) -> None:
        """Method to delete an edge

        :param str edge_id: The id of the edge you want to delete
        """
        self.__edges.delete_edge(edge_id)

    def compute_reference_edges(self) -> None:
        """Method to mark all edges that should be in the final rm_graph
        """

        self.__edges.compute_reference_edges(self.nodes)

    def to_lxml_element(self, view_name: str = None, root_element: etree.Element = None) -> etree.Element:
        """Method to compute etree.Element for the graph. This is necessary if you want to create the ArchiMate xml file.
        This element isn't ArchiMate valid!

        :param view_name: Name of the view.
        :param root_element: The root element.
        :return: root_element
        :rtype: etree.Element
        """

        # define namespace and schemaLocation for the root_element
        xmlns = 'http://www.opengroup.org/xsd/archimate/3.0/'
        xsi = 'http://www.w3.org/2001/XMLSchema-instance'
        xml = 'http://www.w3.org/XML/1998/namespace'
        schema_location = 'http://www.opengroup.org/xsd/archimate/3.0/ ' \
                          'http://www.opengroup.org/xsd/archimate/3.0/archimate3_Diagram.xsd'
        # check if a root_element already exists. This is the case if you create a root_element with multiple views
        if root_element is None:
            # generate a unique id for the root_element
            identifier = generate_unique_key()
            # initiate the root_element with the required attributes.
            # The name of the root_element is {http://www.opengroup.org/xsd/archimate/3.0/}model
            root_element = etree.Element('{' + xmlns + '}model',
                                         attrib={'{' + xsi + '}schemaLocation': schema_location},
                                         nsmap={'xsi': xsi, None: xmlns},
                                         identifier=identifier)
            # create the subelement 'name' with the required attributes for the root_element
            name = etree.SubElement(root_element, 'name', attrib={'{' + xml + '}lang': 'de'}, nsmap={'xml': xml})
            # add text to the subelement 'name'
            name.text = 'reference model'
            # create the subelements 'elements' and 'relationships' with the required attributes for the root_element
            etree.SubElement(root_element, 'elements')
            etree.SubElement(root_element, 'relationships')
            # check if a view name is given.
            # If this is the case create the subelement 'views' and the subsubelement 'diagrams'
            if view_name is not None:
                views = etree.SubElement(root_element, 'views')
                etree.SubElement(views, 'diagrams')
        # check if a view name is given.
        view = None
        if view_name is not None:
            # check if a view with th given name exists
            if len(root_element.xpath('./views/diagrams/view/name[text()="' + view_name + '"]')) == 0:
                # create a unique id for the 'new' view
                view_id = generate_unique_key()
                # get the subelement diagram of the root_element
                diagram = root_element.find('./views/diagrams')
                # create the subelement 'view' with all required attributes and add text
                view = etree.SubElement(diagram, 'view', attrib={'identifier': view_id, '{' + xsi + '}type': 'Diagram'},
                                        nsmap={'xsi': xsi})
                view_name_element = etree.SubElement(view, 'name', attrib={'{' + xml + '}lang': 'de'},
                                                     nsmap={'xml': xml})
                view_name_element.text = view_name
            else:
                # get the view element if the view name already exists
                view_name_element = root_element.xpath('./views/diagrams/view/name[text()="' + view_name + '"]')[0]
                view = view_name_element.find('../')
        # get the nodes and edges of the current graph
        nodes = self.nodes
        edges = self.edges

        # get the subelement 'elements' of the root_element
        elements = root_element.find('./elements')
        # iterate through all nodes and get the index and the row
        for index, row in nodes.iterrows():
            # ignore nodes where the label and the type is None (the root_node)
            tmp = element_to_xml_string(root_element)
            if row['label'] is None and row['type'] is None:
                continue
            # check if the node already in the element
            if root_element.find('./elements/element[@identifier=\'%s\']' %index) is not None:
                # check if a view should be created
                if view_name is not None:
                    # add the node to the view element
                    add_view_node(view, index, xsi)
                    continue
                else:
                    # continue if the node is already part of the element and a view inst wanted
                    continue
            # create a new subelement 'element' of element 'elements' (add the node to the elements)
            sub_element = etree.SubElement(elements, 'element',
                                           attrib={'identifier': index, '{' + xsi + '}type': row['type'],
                                                   '{' + xml + '}lang': 'de'},
                                           nsmap={'xml': xml, 'xsi': xsi, None: xmlns})
            # add the name to the element
            sub_element_name = etree.SubElement(sub_element, 'name', attrib={"{" + xml + '}lang': 'de'},
                                                nsmap={'xml': xml})
            # add the node-label to the element
            sub_element_name.text = row['label']
            # add the node to the view if required
            if view_name is not None:
                add_view_node(view, index, xsi)

        # get the relationships subelement
        relationships = root_element.find('./relationships')
        # iterate over all edges of the graph
        for index, row in edges.iterrows():
            # get the type, the source and the target of the current edge(row)
            relation_type = row['type']
            relation_source = row['source']
            relation_target = row['target']
            # continue if the edge is aroot edge
            if relation_type == 'root_edge':
                continue
            # check if the relationship (edge is already part of the root_element
            if root_element.find('./relationships/relationship[@identifier=\'%s\']' % index) is not None:
                # check if a view should be createt. If this is the case add the edge to the element
                if view_name is not None:
                    add_view_connection(view, index, relation_source, relation_target, xsi)
                    continue
                else:
                    continue
            # add edge to the root_element if its already inserted
            # get the source_element from the element tag of the root_element by the identifier
            source_element = root_element.find("./elements/element[@identifier='%s']" % relation_source)
            # check if the element exists, if not raise a exception
            if len(source_element) is 0:
                raise Exception("source_element does not exist")
            # get the id of the source_element
            source_id = source_element.get('identifier')
            # get the target_element from the element tag of the root_element by the identifier
            target_element = root_element.find("./elements/element[@identifier='%s']" % relation_target)
            # check if the element exists, if not raise a exception
            if len(target_element) is 0:
                raise Exception("target_element does not exist")
            # get the id of the source_element
            target_id = target_element.get('identifier')
            # add a new relationship with all required attributes under the relationships tag
            etree.SubElement(relationships, "relationship", identifier=index,
                             source=source_id,
                             target=target_id,
                             attrib={"{" + xsi + "}type": row['type'],
                                     "{" + xml + "}lang": 'de'},
                             nsmap={"xml": xml})
            # create a connection under the view tag if a view should be created
            if view_name is not None:
                add_view_connection(view, index, relation_source, relation_target, xsi)
        # return the created or updated root_element
        return root_element

    @staticmethod
    def recreate_identifier(root_element) -> etree.Element:
        return recreate_identifier(root_element)

    @staticmethod
    def element_to_xml_string(root_element) -> str:
        return element_to_xml_string(root_element)

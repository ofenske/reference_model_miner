from lxml import etree
import string
import random

CHARACTERS = (
        string.ascii_letters
        + string.digits
        + '-._'
)
CHARACTER = (string.ascii_letters)


def generate_unique_key() -> str:
    """Method to compute a 32 characters long unique key which is ncname valid

    :return: unique_key
    :rtype: str
    """
    return ''.join(random.sample(CHARACTER, 1)) + ''.join(random.sample(CHARACTERS, 31))


def recreate_identifier(root_element) -> etree.Element:
    """Method to update the identifiers of a etree.Element to ncname valid keys.
    This is required if you want to creat a ArchiMate model

    :return: root_element
    :rtype: etree.Element
    """
    # get all elements from the root_element
    elements = root_element.findall("./elements/element")
    # get all relationships from the root_element
    relationships = root_element.findall("./relationships/relationship")
    # iterate through all element nodes
    for relationship in elements:
        # get the current (false) id
        old_id = relationship.get("identifier")
        # update the id
        new_id = generate_unique_key()
        relationship.attrib["identifier"] = new_id
        # get all relations with the old element id in the source or target attribute
        ids_to_update = root_element.findall("./relationships/relationship[@source='" + old_id + "']")
        ids_to_update.extend(root_element.findall("./relationships/relationship[@target='" + old_id + "']"))
        # iterate through these relations and update the identifiers of the source and the target
        for id_to_update in ids_to_update:
            if id_to_update.attrib["source"] == old_id:
                id_to_update.attrib["source"] = new_id
            if id_to_update.attrib["target"] == old_id:
                id_to_update.attrib["target"] = new_id
        # get all view from the root_element
        views_to_update = root_element.findall("./views/diagrams/view")
        # iterate through each view
        for current_view in views_to_update:
            # get the name of the current view
            view_name = current_view.find("./name").text
            # get all nodes from the view wher the id is the old identifier
            view_ids_to_update = current_view.findall("./node[@elementRef='" + old_id + "']")
            # iterate through these nodes
            for id_to_update in view_ids_to_update:
                # update the elementRef
                id_to_update.attrib["elementRef"] = new_id
                # the identifier of the current view
                view_id = id_to_update.attrib["identifier"]
                # get all connections of the view where the node is the target or the source
                view_connections = root_element.xpath(
                    "./views/diagrams/view/name[text()='" + view_name + "']"
                     "/../connection[@source='" + old_id + "']")
                view_connections.extend(root_element.xpath(
                    "./views/diagrams/view/name[text()='" + view_name + "']"
                     "/../connection[@target='" + old_id + "']"))
                # iterate through the connections and update the source and/or target
                for view_connection in view_connections:
                    if view_connection.attrib["source"] == old_id:
                        view_connection.attrib["source"] = view_id
                    if view_connection.attrib["target"] == old_id:
                        view_connection.attrib["target"] = view_id
    # iterate through all relationships
    for relationship in relationships:
        # get the old identifier of the relationship
        old_id = relationship.get("identifier")
        # generate a new identifier
        new_id = generate_unique_key()
        # update the identifier of the relationship
        relationship.attrib["identifier"] = new_id
        # get all connections of a view where the relationshipRef is the old id
        view_ids_to_update = root_element.findall(
            "./views/diagrams/view/connection[@relationshipRef='" + old_id + "']")
        # iterate through these connections and update the relationshipRef
        for view_id_to_update in view_ids_to_update:
            view_id_to_update.attrib["relationshipRef"] = new_id
    # return the root_element which is now ncname valid
    return root_element


def add_style(node_element) -> None:
    """Method to compute the sytle tag of the node_element

    :return: None
    :rtype: None
    """
    # create the style subelement
    style = etree.SubElement(node_element, 'style')
    # add line color and/or fill color subelements with all required attributes
    if node_element.tag == 'node':
        etree.SubElement(style, 'fillColor', attrib={'r': '255', 'g': '255', 'b': '181', 'a': '100'})
        etree.SubElement(style, 'lineColor', attrib={'r': '92', 'g': '92', 'b': '92'})
    elif node_element.tag == 'connection':
        etree.SubElement(style, 'lineColor', attrib={'r': '0', 'g': '0', 'b': '0'})
    # add font subelement
    font = etree.SubElement(style, 'font', attrib={'name': 'Segoe UI', 'size': '9'})
    # add color subelement to font element
    etree.SubElement(font, 'color', attrib={'r': '0', 'g': '0', 'b': '0'})


def add_view_node(view, index, xsi) -> None:
    """Method to add a node to a view.

    :return: None
    :rtype: None
    """
    # create the node subelement with all attributes
    view_node = etree.SubElement(view, 'node',
                                 attrib={'identifier': generate_unique_key(), 'elementRef': index,
                                         '{' + xsi + '}type': 'Element', 'x': '100', 'y': '100', 'w': '100',
                                         'h': '100'}, nsmap={'xsi': xsi})
    # add the style to the node
    add_style(view_node)


def add_view_connection(view, index, source, target, xsi) -> None:
    """Method to add a connection to a view.

    :return: None
    :rtype: None
    """
    # create the connection subelement with all attributes
    view_connection = etree.SubElement(view, 'connection', attrib={'identifier': generate_unique_key(),
                                                                   '{' + xsi + '}type': 'Relationship',
                                                                   'relationshipRef': index, 'source': source,
                                                                   'target': target})
    # add the style to the node
    add_style(view_connection)


def element_to_xml_string(element) -> str:
    """Method to compute the xml string of a etree.Element

    :return: element_string
    :rtype: str
    """
    # create the string with utf-8 encoding, pretty print and the xml declaration
    element_string = etree.tostring(element, encoding="utf-8", xml_declaration=True, pretty_print=True) \
        .decode("utf-8")
    # return string
    return element_string

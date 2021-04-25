from unittest import TestCase
from core.loader.data_loader import *

class TestDataLoader (TestCase):
    def test_get_view_nodes(self):
        expected = [{'id1': ['id2', 'id4'], 'id3': [], 'id2': ['id6'], 'id4': [], 'id6': []}, {'id1': [], 'id5': []}]

        data_loader = DataLoader()
        test_data = data_loader.load_file(r'..\..\data\test_data\test_better.xml')
        test_views = data_loader.get_all_views(test_data)
        views_nodes = []
        for view in test_views:
            view_nodes = data_loader.get_view_nodes(view)
            views_nodes.append(view_nodes)
        print('\n', expected)
        print(views_nodes)
        self.assertEqual(str(expected), str(views_nodes))

    def test_get_all_view_edges_objects(self):
        expected = pd.DataFrame.from_dict({"id-6aeb6811-19c2-49ba-9787-9623830aab6f": ["id1", "id2", "Composition"],
                                           "id-62cae331-851a-4d95-9ebc-bb4b1d514bde": ["id3", "id1", "Aggregation"],
                                           "id-d1ecff24-6e3b-40b4-921a-417c010b22ad": ["id1", "id4", "Aggregation"],
                                           "test2_has_child_test6": ["id2", "id6", "Aggregation"]},
                                          orient='index', columns=['source', 'target', 'type'])

        data_loader = DataLoader()
        doc = data_loader.load_file(r'..\..\data\test_data\test3.xml')
        view_edges = ['id-0bcab9c6-4e24-4a1a-8b7d-6cfd2ba07e7d', 'id-11c418b8-5a76-4d94-b2e7-06e56e06383c']
        view_nodes = {'id-444d212e-d33d-4e93-9cf6-12b2a2df457e': ['id-670adf59-0c34-4d4a-9b60-402b697fc569'],
                      'id-08b5888d-d272-4a11-9764-882d40d9275f': [],
                      'id-b4047819-67a9-447b-88e5-5c044eda0135': []}
        view_edges_objects = data_loader.get_all_view_edges_objects(doc, view_edges, view_nodes)
        #print('\n', expected)
        print(view_edges_objects)
        #self.assertEqual(expected.to_string(), view_edges_objects.to_string())


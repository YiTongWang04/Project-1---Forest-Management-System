import unittest
from unittest.mock import patch, MagicMock
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus

class TestForestGraphComprehensive(unittest.TestCase):
    def setUp(self):
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.AT_RISK)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree3, 15.2)
        self.forest = ForestGraph()

    def test_add_tree_success(self):
        self.forest.add_tree(self.tree1)
        self.assertIn(self.tree1, self.forest.adjacency)

    def test_add_duplicate_tree(self):
        self.forest.add_tree(self.tree1)
        with self.assertRaises(ValueError):
            self.forest.add_tree(self.tree1)

    def test_remove_existing_tree(self):
        self.forest.add_tree(self.tree1)
        self.forest.remove_tree(self.tree1)
        self.assertNotIn(self.tree1, self.forest.adjacency)

    def test_remove_nonexistent_tree(self):
        with self.assertRaises(ValueError):
            self.forest.remove_tree(self.tree1)

    def test_add_path_success(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        
        found = False
        seen = set()
        for edges in self.forest.adjacency.values():
            for edge in edges:
                eid = tuple(sorted([edge.tree1.tree_id, edge.tree2.tree_id]))
                if eid not in seen:
                    seen.add(eid)
                    if edge == self.path1:
                        found = True
        self.assertTrue(found)

    def test_add_path_with_missing_tree(self):
        self.forest.add_tree(self.tree1)
        with self.assertRaises(ValueError):
            self.forest.add_path(self.path1)

    def test_add_duplicate_path(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        with self.assertRaises(ValueError):
            self.forest.add_path(self.path1)

    def test_remove_existing_path(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        self.forest.remove_path(self.path1)
        
        found = False
        seen = set()
        for edges in self.forest.adjacency.values():
            for edge in edges:
                eid = tuple(sorted([edge.tree1.tree_id, edge.tree2.tree_id]))
                if eid not in seen:
                    seen.add(eid)
                    if edge == self.path1:
                        found = True
        self.assertFalse(found)

    def test_remove_nonexistent_path(self):
        with self.assertRaises(ValueError):
            self.forest.remove_path(self.path1)

    def test_update_tree_health_success(self):
        self.forest.add_tree(self.tree1)
        self.forest.update_tree_health(self.tree1, HealthStatus.INFECTED)
        self.assertEqual(self.tree1.health_status, HealthStatus.INFECTED)

    def test_update_nonexistent_tree_health(self):
        with self.assertRaises(ValueError):
            self.forest.update_tree_health(self.tree1, HealthStatus.INFECTED)

    def test_update_path_distance_success(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        self.forest.update_path_distance(self.path1, 20.0)
        self.assertEqual(self.path1.distance, 20.0)

    def test_update_nonexistent_path_distance(self):
        with self.assertRaises(ValueError):
            self.forest.update_path_distance(self.path1, 20.0)

    def test_repr_empty_forest(self):
        repr_str = repr(self.forest).strip().replace("\n\n", "\n")
        self.assertEqual(repr_str, "Nodes:\nEdges:")

    def test_repr(self):
        repr_str = repr(self.forest)
        normalized_str = repr_str.replace("\n\n", "\n").strip()
        self.assertRegex(normalized_str, r"^Nodes:.*\nEdges:.*$")

    @patch('forest_management.core.forest_graph.TreeNode')
    def test_add_tree_with_mock(self, mock_tree_node):
        mock_tree = MagicMock()
        mock_tree_node.return_value = mock_tree
        self.forest.add_tree(mock_tree)
        self.assertIn(mock_tree, self.forest.adjacency)

if __name__ == '__main__':
    unittest.main()

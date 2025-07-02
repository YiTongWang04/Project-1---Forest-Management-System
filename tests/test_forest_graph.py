import unittest
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus

class TestForestGraph(unittest.TestCase):
    def setUp(self):
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.AT_RISK)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree3, 15.2)
        self.forest = ForestGraph()

    def test_add_tree(self):
        self.forest.add_tree(self.tree1)
        self.assertIn(self.tree1, self.forest.nodes)

    def test_remove_tree(self):
        self.forest.add_tree(self.tree1)
        self.forest.remove_tree(self.tree1)
        self.assertNotIn(self.tree1, self.forest.nodes)

    def test_add_path(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        self.assertIn(self.path1, self.forest.edges)

    def test_remove_path(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        self.forest.remove_path(self.path1)
        self.assertNotIn(self.path1, self.forest.edges)

    def test_update_tree_health(self):
        self.forest.add_tree(self.tree1)
        self.forest.update_tree_health(self.tree1, HealthStatus.INFECTED)
        self.assertEqual(self.tree1.health_status, HealthStatus.INFECTED)

    def test_update_path_distance(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        self.forest.update_path_distance(self.path1, 20.0)
        self.assertEqual(self.path1.distance, 20.0)

    def test_repr(self):
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_path(self.path1)
        expected_output = (
            f"Nodes:\n{self.tree1}\n{self.tree2}\n"
            f"Edges:\n{self.path1}"
        )
        self.assertEqual(repr(self.forest), expected_output)

if __name__ == '__main__':
    unittest.main()
import unittest
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus
from forest_management.tasks.conservation_areas import find_conservation_areas

class TestConservationAreas(unittest.TestCase):
    def setUp(self):
        self.forest = ForestGraph()
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.AT_RISK)
        self.tree4 = TreeNode(4, "Oak", 20, HealthStatus.HEALTHY)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree4, 15.2)
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_tree(self.tree3)
        self.forest.add_tree(self.tree4)
        self.forest.add_path(self.path1)
        self.forest.add_path(self.path2)

    def test_find_conservation_areas(self):
        areas = find_conservation_areas(self.forest)
        self.assertEqual(len(areas), 1)
        self.assertIn(self.tree1, areas[0])
        self.assertIn(self.tree2, areas[0])
        self.assertIn(self.tree4, areas[0])
        self.assertNotIn(self.tree3, areas[0])

if __name__ == '__main__':
    unittest.main()
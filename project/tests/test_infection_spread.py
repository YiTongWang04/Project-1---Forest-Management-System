import unittest
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus
from forest_management.tasks.infection_spread import simulate_infection_spread

class TestInfectionSpread(unittest.TestCase):
    def setUp(self):
        self.forest = ForestGraph()
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.HEALTHY)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree3, 15.2)
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_tree(self.tree3)
        self.forest.add_path(self.path1)
        self.forest.add_path(self.path2)

    def test_simulate_infection_spread(self):
        simulate_infection_spread(self.forest, self.tree1)
        self.assertEqual(self.tree1.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree2.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree3.health_status, HealthStatus.INFECTED)

if __name__ == '__main__':
    unittest.main()
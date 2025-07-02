import unittest
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus
from forest_management.tasks.path_finding import find_shortest_path

class TestShortestPath(unittest.TestCase):
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

    def test_find_shortest_path(self):
        path, distance = find_shortest_path(self.forest, self.tree1, self.tree3)  # 解构返回的元组
        self.assertAlmostEqual(distance, 25.7)  # 检查距离
        self.assertEqual(len(path), 3)  # 检查路径长度
        self.assertIn(self.tree1, path)  # 检查路径是否包含起点
        self.assertIn(self.tree2, path)  # 检查路径是否包含中间节点
        self.assertIn(self.tree3, path)  # 检查路径是否包含终点

if __name__ == '__main__':
    unittest.main()
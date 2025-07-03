import unittest
from unittest.mock import patch, MagicMock
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus
from forest_management.tasks.infection_spread import simulate_infection_spread

class TestInfectionSpread(unittest.TestCase):
    def setUp(self):
        # 基础测试数据
        self.forest = ForestGraph()
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.HEALTHY)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree3, 15.2)
        
        # 添加隔离的树
        self.isolated_tree = TreeNode(4, "Birch", 25, HealthStatus.HEALTHY)
        
        # 添加已感染的树
        self.infected_tree = TreeNode(5, "Willow", 35, HealthStatus.INFECTED)
        self.healthy_tree = TreeNode(6, "Redwood", 60, HealthStatus.HEALTHY)
        self.infected_path = TreePath(self.infected_tree, self.healthy_tree, 8.0)
        
        # 构建测试森林
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_tree(self.tree3)
        self.forest.add_tree(self.isolated_tree)
        self.forest.add_tree(self.infected_tree)
        self.forest.add_tree(self.healthy_tree)
        self.forest.add_path(self.path1)
        self.forest.add_path(self.path2)
        self.forest.add_path(self.infected_path)

    def test_basic_infection_spread(self):
        """测试基本感染传播"""
        result = simulate_infection_spread(self.forest, self.tree1)
        self.assertEqual(self.tree1.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree2.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree3.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.isolated_tree.health_status, HealthStatus.HEALTHY)
        self.assertEqual(len(result), 3)

    def test_starting_from_infected_tree(self):
        """测试从已感染的树开始传播"""
        result = simulate_infection_spread(self.forest, self.infected_tree)
        self.assertEqual(self.healthy_tree.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree1.health_status, HealthStatus.HEALTHY)
        self.assertEqual(len(result), 2)

    def test_no_spread_to_isolated_tree(self):
        """测试不会传播到孤立的树"""
        result = simulate_infection_spread(self.forest, self.tree1)
        self.assertEqual(self.isolated_tree.health_status, HealthStatus.HEALTHY)
        self.assertEqual(len(result), 3)

    def test_already_infected_tree(self):
        """测试已经感染的树作为起点时会抛出异常"""
        self.infected_tree.health_status = HealthStatus.INFECTED
        with self.assertRaises(ValueError):
            simulate_infection_spread(self.forest, self.infected_tree)

    def test_empty_forest(self):
        """测试空森林"""
        empty_forest = ForestGraph()
        # 明确测试空森林和None起始树的情况
        with self.assertRaises(ValueError) as cm:
            simulate_infection_spread(empty_forest, None)
        self.assertEqual(str(cm.exception), "起始树不能为空")

    def test_invalid_start_tree(self):
        """测试无效的起始树"""
        # 测试None起始树
        with self.assertRaises(ValueError) as cm:
            simulate_infection_spread(self.forest, None)
        self.assertEqual(str(cm.exception), "起始树不能为空")
        
        # 测试不在森林中的树
        non_existent_tree = TreeNode(999, "Non-existent", 0, HealthStatus.HEALTHY)
        with self.assertRaises(ValueError) as cm:
            simulate_infection_spread(self.forest, non_existent_tree)
        self.assertEqual(str(cm.exception), "起始树不在森林中")

    def test_starting_from_infected_tree(self):
        """测试从已感染的树开始传播"""
        self.infected_tree.health_status = HealthStatus.INFECTED
        with self.assertRaises(ValueError):
            simulate_infection_spread(self.forest, self.infected_tree)

    def test_different_speeds(self):
        """测试不同传播速度"""
        # 创建第一个森林用于慢速传播测试
        forest_slow = ForestGraph()
        t1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        t2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        forest_slow.add_tree(t1)
        forest_slow.add_tree(t2)
        forest_slow.add_path(TreePath(t1, t2, 10))
        result_slow = simulate_infection_spread(forest_slow, t1, speed=0.1)

        # 创建第二个森林用于快速传播测试
        forest_fast = ForestGraph()
        t1b = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        t2b = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        forest_fast.add_tree(t1b)
        forest_fast.add_tree(t2b)
        forest_fast.add_path(TreePath(t1b, t2b, 10))
        result_fast = simulate_infection_spread(forest_fast, t1b, speed=10)

        # 断言慢速传播的时间大于快速传播的时间
        self.assertGreater(result_slow[1][1], result_fast[1][1])

    def test_return_value_format(self):
        """测试返回值格式"""
        result = simulate_infection_spread(self.forest, self.tree1)
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIsInstance(item[0], TreeNode)
            self.assertIsInstance(item[1], float)

    # 新增测试用例来提高覆盖率
    def test_invalid_forest_type(self):
        """测试无效的森林类型"""
        with self.assertRaises(TypeError) as cm:
            simulate_infection_spread("not a forest", self.tree1)
        self.assertEqual(str(cm.exception), "forest参数必须是ForestGraph类型")

    def test_invalid_start_tree_type(self):
        """测试无效的起始树类型"""
        with self.assertRaises(TypeError) as cm:
            simulate_infection_spread(self.forest, "not a tree")
        self.assertEqual(str(cm.exception), "start_tree参数必须是TreeNode类型")

    def test_invalid_speed(self):
        """测试无效的传播速度"""
        with self.assertRaises(ValueError) as cm:
            simulate_infection_spread(self.forest, self.tree1, speed=0)
        self.assertEqual(str(cm.exception), "传播速度必须大于0")

    def test_negative_speed(self):
        """测试负传播速度"""
        with self.assertRaises(ValueError) as cm:
            simulate_infection_spread(self.forest, self.tree1, speed=-1)
        self.assertEqual(str(cm.exception), "传播速度必须大于0")

    def test_single_tree_forest(self):
        """测试只有一棵树的森林"""
        single_tree_forest = ForestGraph()
        single_tree = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        single_tree_forest.add_tree(single_tree)
        
        result = simulate_infection_spread(single_tree_forest, single_tree)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], single_tree)
        self.assertEqual(result[0][1], 0.0)

    def test_forest_with_all_infected_trees(self):
        """测试所有树都已感染的森林"""
        all_infected_forest = ForestGraph()
        infected_tree1 = TreeNode(1, "Oak", 50, HealthStatus.INFECTED)
        infected_tree2 = TreeNode(2, "Pine", 30, HealthStatus.INFECTED)
        all_infected_forest.add_tree(infected_tree1)
        all_infected_forest.add_tree(infected_tree2)
        all_infected_forest.add_path(TreePath(infected_tree1, infected_tree2, 10))
        
        # 应该抛出异常，因为起始树已经是感染状态
        with self.assertRaises(ValueError):
            simulate_infection_spread(all_infected_forest, infected_tree1)

    def test_forest_with_disconnected_components(self):
        """测试有多个连通分量的森林"""
        disconnected_forest = ForestGraph()
        tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        tree3 = TreeNode(3, "Maple", 40, HealthStatus.HEALTHY)
        tree4 = TreeNode(4, "Birch", 25, HealthStatus.HEALTHY)
        
        disconnected_forest.add_tree(tree1)
        disconnected_forest.add_tree(tree2)
        disconnected_forest.add_tree(tree3)
        disconnected_forest.add_tree(tree4)
        disconnected_forest.add_path(TreePath(tree1, tree2, 10))
        disconnected_forest.add_path(TreePath(tree3, tree4, 15))
        
        result = simulate_infection_spread(disconnected_forest, tree1)
        self.assertEqual(tree1.health_status, HealthStatus.INFECTED)
        self.assertEqual(tree2.health_status, HealthStatus.INFECTED)
        self.assertEqual(tree3.health_status, HealthStatus.HEALTHY)
        self.assertEqual(tree4.health_status, HealthStatus.HEALTHY)
        self.assertEqual(len(result), 2)

    def test_result_sorting(self):
        """测试结果按时间排序"""
        result = simulate_infection_spread(self.forest, self.tree1)
        # 检查结果是否按时间排序
        for i in range(len(result) - 1):
            self.assertLessEqual(result[i][1], result[i + 1][1])

    def test_time_rounding(self):
        """测试时间四舍五入到两位小数"""
        result = simulate_infection_spread(self.forest, self.tree1)
        for _, time in result:
            # 检查时间是否被四舍五入到两位小数
            rounded_time = round(time, 2)
            self.assertEqual(time, rounded_time)

if __name__ == '__main__':
    unittest.main()
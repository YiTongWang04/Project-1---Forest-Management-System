import pandas as pd
from enum import Enum, auto
from collections import defaultdict

# 定义健康状态的枚举
class HealthStatus(Enum):
    HEALTHY = auto()  # 健康
    INFECTED = auto()  # 感染
    AT_RISK = auto()  # 有风险

# 树节点类
class TreeNode:
    def __init__(self, tree_id, species, age, health_status):
        self.tree_id = tree_id  # 树木 ID
        self.species = species  # 树种
        self.age = age  # 树龄
        if not isinstance(health_status, HealthStatus):
            raise ValueError("health_status 必须是 HealthStatus 枚举的实例")
        self.health_status = health_status  # 健康状态

    def __repr__(self):
        # 返回树的字符串表示
        return (f"TreeNode(ID={self.tree_id}, Species={self.species}, Age={self.age}, "
                f"Health={self.health_status.name})")

    def __eq__(self, other):
        # 比较两个树节点是否相等（基于 tree_id）
        return self.tree_id == other.tree_id

    def __lt__(self, other):
        # 比较两个树节点的大小（基于 tree_id）
        return self.tree_id < other.tree_id

# 树路径类
class TreePath:
    def __init__(self, tree1, tree2, distance):
        if tree1 == tree2:
            raise ValueError("路径不能连接同一棵树")
        self.tree1 = tree1  # 路径连接的第一棵树
        self.tree2 = tree2  # 路径连接的第二棵树
        self.distance = distance  # 两棵树之间的距离

    def __repr__(self):
        # 返回路径的字符串表示
        return (f"TreePath({self.tree1.tree_id} <-> {self.tree2.tree_id}, "
                f"Distance={self.distance})")

    def __eq__(self, other):
        # 比较两条路径是否相等（不区分方向）
        return (self.tree1 == other.tree1 and self.tree2 == other.tree2) or \
               (self.tree1 == other.tree2 and self.tree2 == other.tree1)

# 森林图类
class ForestGraph:
    def __init__(self):
        self.nodes = set()  # 存储所有树节点
        self.edges = set()  # 存储所有路径

    def add_tree(self, tree):
        # 添加树节点
        if tree in self.nodes:
            raise ValueError("树已存在于森林中")
        self.nodes.add(tree)

    def remove_tree(self, tree):
        # 删除树节点
        if tree not in self.nodes:
            raise ValueError("树不存在于森林中")
        self.nodes.remove(tree)
        # 同时删除与该树相关的所有路径
        self.edges = {edge for edge in self.edges if edge.tree1 != tree and edge.tree2 != tree}

    def add_path(self, path):
        # 添加路径
        if path.tree1 not in self.nodes or path.tree2 not in self.nodes:
            raise ValueError("路径连接的两棵树都必须存在于森林中")
        if path in self.edges:
            raise ValueError("路径已存在")
        self.edges.add(path)

    def remove_path(self, path):
        # 删除路径
        if path not in self.edges:
            raise ValueError("路径不存在")
        self.edges.remove(path)

    def update_tree_health(self, tree, new_health_status):
        # 更新树的健康状态
        if tree not in self.nodes:
            raise ValueError("树不存在于森林中")
        if not isinstance(new_health_status, HealthStatus):
            raise ValueError("new_health_status 必须是 HealthStatus 枚举的实例")
        tree.health_status = new_health_status

    def update_path_distance(self, path, new_distance):
        # 更新路径的距离
        if path not in self.edges:
            raise ValueError("路径不存在")
        path.distance = new_distance

    def __repr__(self):
        # 返回森林的字符串表示
        nodes_str = "\n".join(repr(node) for node in self.nodes)
        edges_str = "\n".join(repr(edge) for edge in self.edges)
        return f"Nodes:\n{nodes_str}\nEdges:\n{edges_str}"

# 加载数据集函数
def load_forest_data(trees_file_path, paths_file_path):
    forest = ForestGraph()
    trees_df = pd.read_excel(trees_file_path)
    paths_df = pd.read_excel(paths_file_path)

    # 创建树节点
    for index, row in trees_df.iterrows():
        tree_id = row['tree_id']
        species = row['species']
        age = row['age']
        # 确保Excel中的health_status值与枚举值完全匹配(HEALTHY/INFECTED/AT_RISK)
        health_status = HealthStatus[row['health_status'].upper().replace(" ", "_")] 
        tree = TreeNode(tree_id, species, age, health_status)
        forest.add_tree(tree)

    # 创建路径
    for index, row in paths_df.iterrows():
        tree_id1 = row['tree_1']  # 修改为 tree_1
        tree_id2 = row['tree_2']  # 修改为 tree_2
        distance = row['distance']
        tree1 = next((tree for tree in forest.nodes if tree.tree_id == tree_id1), None)
        tree2 = next((tree for tree in forest.nodes if tree.tree_id == tree_id2), None)
        if tree1 and tree2:
            path = TreePath(tree1, tree2, distance)
            forest.add_path(path)

    return forest

# 测试代码（使用 unittest）
import unittest

class TestForestGraph(unittest.TestCase):
    def setUp(self):
        # 初始化测试数据
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

class TestLoadForestData(unittest.TestCase):
    def test_load_forest_data(self):
        trees_file_path = r"D:\python\2024秋小学期\森林\forest_management_dataset-trees .csv"
        paths_file_path = r"D:\python\2024秋小学期\森林\forest_management_dataset-paths.csv"
        forest = load_forest_data(trees_file_path, paths_file_path)
        self.assertIsNotNone(forest)
        self.assertIsInstance(forest, ForestGraph)

if __name__ == '__main__':
    unittest.main()
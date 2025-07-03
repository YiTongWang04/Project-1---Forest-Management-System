import sys
sys.path.append('d:/python/2024秋小学期/森林/Project-1---Forest-Management-System/project')

from forest_management.core.tree_node import HealthStatus, TreeNode
from forest_management.core.tree_path import TreePath
from collections import defaultdict

class ForestGraph:
    def __init__(self):
        self.adjacency = defaultdict(list)  # 邻接表 {TreeNode: list[TreePath]}

    def add_tree(self, tree):
        """添加一棵树到森林中"""
        if tree in self.adjacency:
            raise ValueError("树已存在于森林中")
        self.adjacency[tree] = []

    def remove_tree(self, tree):
        """从森林中移除一棵树"""
        if tree not in self.adjacency:
            raise ValueError("树不存在于森林中")
        # 删除与该树相关的所有路径
        for path in self.adjacency[tree]:
            other_tree = path.tree1 if path.tree2 == tree else path.tree2
            self.adjacency[other_tree].remove(path)
        del self.adjacency[tree]

    def add_path(self, path):
        """添加一条路径到森林中"""
        if path.tree1 not in self.adjacency or path.tree2 not in self.adjacency:
            raise ValueError("路径连接的两棵树都必须存在于森林中")
        if path in self.adjacency[path.tree1] or path in self.adjacency[path.tree2]:
            raise ValueError("路径已存在")
        self.adjacency[path.tree1].append(path)
        self.adjacency[path.tree2].append(path)

    def remove_path(self, path):
        """从森林中移除一条路径"""
        if path not in self.adjacency[path.tree1] or path not in self.adjacency[path.tree2]:
            raise ValueError("路径不存在")
        self.adjacency[path.tree1].remove(path)
        self.adjacency[path.tree2].remove(path)

    def update_tree_health(self, tree, new_health_status):
        """更新树的健康状态"""
        if tree not in self.adjacency:
            raise ValueError("树不存在于森林中")
        tree.health_status = new_health_status

    def update_path_distance(self, path, new_distance):
        """更新路径的距离"""
        if path not in self.adjacency[path.tree1] or path not in self.adjacency[path.tree2]:
            raise ValueError("路径不存在")
        path.distance = new_distance

    def __repr__(self):
        nodes_str = "\n".join(repr(node) for node in self.adjacency.keys())
        seen = set()
        edges_str = ""
        for edges in self.adjacency.values():
            for edge in edges:
                eid = tuple(sorted([edge.tree1.tree_id, edge.tree2.tree_id]))
                if eid not in seen:
                    seen.add(eid)
                    edges_str += repr(edge) + "\n"
        return f"Nodes:\n{nodes_str}\nEdges:\n{edges_str.strip()}"
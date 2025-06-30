import sys
sys.path.append('d:/python/2024秋小学期/森林/Project-1---Forest-Management-System/project')
from forest_management.core.tree_node import HealthStatus, TreeNode
from forest_management.core.tree_path import TreePath 

class ForestGraph:
    def __init__(self):
        self.nodes = set()
        self.edges = set()

    def add_tree(self, tree):
        if tree in self.nodes:
            raise ValueError("树已存在于森林中")
        self.nodes.add(tree)

    def remove_tree(self, tree):
        if tree not in self.nodes:
            raise ValueError("树不存在于森林中")
        self.nodes.remove(tree)
        self.edges = {edge for edge in self.edges if edge.tree1 != tree and edge.tree2 != tree}

    def add_path(self, path):
        if path.tree1 not in self.nodes or path.tree2 not in self.nodes:
            raise ValueError("路径连接的两棵树都必须存在于森林中")
        if path in self.edges:
            raise ValueError("路径已存在")
        self.edges.add(path)

    def remove_path(self, path):
        if path not in self.edges:
            raise ValueError("路径不存在")
        self.edges.remove(path)

    def update_tree_health(self, tree, new_health_status):
        if tree not in self.nodes:
            raise ValueError("树不存在于森林中")
        if not isinstance(new_health_status, HealthStatus):
            raise ValueError("new_health_status 必须是 HealthStatus 枚举的实例")
        tree.health_status = new_health_status

    def update_path_distance(self, path, new_distance):
        if path not in self.edges:
            raise ValueError("路径不存在")
        path.distance = new_distance

    def __repr__(self):
        nodes_str = "\n".join(repr(node) for node in sorted(self.nodes, key=lambda x: x.tree_id))
        edges_str = "\n".join(repr(edge) for edge in sorted(self.edges, key=lambda x: (x.tree1.tree_id, x.tree2.tree_id)))
        return f"Nodes:\n{nodes_str}\nEdges:\n{edges_str}"
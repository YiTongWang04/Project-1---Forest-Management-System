from forest_management.core.forest_graph import ForestGraph
from forest_management.core.tree_node import HealthStatus, TreeNode

def find_conservation_areas(forest: ForestGraph, min_size: int = 1) -> list[list[TreeNode]]:
    """查找森林中的健康树木保护区"""
    visited = set()
    conservation_areas = []

    def dfs(node, area):
        visited.add(node)
        area.append(node)
        for path in forest.adjacency[node]:
            neighbor = path.tree2 if path.tree1 == node else path.tree1
            if neighbor.health_status == HealthStatus.HEALTHY and neighbor not in visited:
                dfs(neighbor, area)

    for tree in forest.adjacency:
        if tree.health_status == HealthStatus.HEALTHY and tree not in visited:
            area = []
            dfs(tree, area)
            if len(area) >= min_size:
                conservation_areas.append(area)

    return conservation_areas
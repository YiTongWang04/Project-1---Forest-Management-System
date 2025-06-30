from forest_management.core.forest_graph import ForestGraph
from forest_management.core.tree_node import HealthStatus
def find_conservation_areas(forest: ForestGraph):
    visited = set()
    conservation_areas = []

    def dfs(node, area):
        if node not in visited:
            visited.add(node)
            area.append(node)
            for edge in forest.edges:
                if edge.tree1 == node:
                    neighbor = edge.tree2
                elif edge.tree2 == node:
                    neighbor = edge.tree1
                else:
                    continue
                if neighbor.health_status == HealthStatus.HEALTHY and neighbor not in visited:
                    dfs(neighbor, area)

    for tree in forest.nodes:
        if tree.health_status == HealthStatus.HEALTHY and tree not in visited:
            area = []
            dfs(tree, area)
            conservation_areas.append(area)
    
    return conservation_areas
import heapq
from forest_management.core.forest_graph import ForestGraph
from forest_management.core.tree_node import TreeNode

def find_shortest_path(
    forest: ForestGraph, 
    start_tree: TreeNode, 
    end_tree: TreeNode
) -> tuple[list[TreeNode], float]:
    """使用Dijkstra算法查找两棵树之间的最短路径"""
    if start_tree not in forest.adjacency or end_tree not in forest.adjacency:
        raise ValueError("起始树或目标树不在森林中")

    distances = {tree: float('inf') for tree in forest.adjacency}
    previous = {tree: None for tree in forest.adjacency}
    distances[start_tree] = 0
    priority_queue = [(0, start_tree)]
    visited = set()

    while priority_queue:
        current_distance, current_tree = heapq.heappop(priority_queue)
        if current_tree in visited:
            continue
        visited.add(current_tree)

        if current_tree == end_tree:
            break

        # 遍历邻接表
        for path in forest.adjacency[current_tree]:
            neighbor = path.tree2 if path.tree1 == current_tree else path.tree1
            new_distance = current_distance + path.distance

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_tree
                heapq.heappush(priority_queue, (new_distance, neighbor))

    # 回溯路径
    path = []
    node = end_tree
    while node:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[end_tree] if distances[end_tree] < float('inf') else float('inf')
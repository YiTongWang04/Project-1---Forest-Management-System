import heapq
from forest_management.core.forest_graph import ForestGraph

def find_shortest_path(forest: ForestGraph, start_tree, end_tree):
    distances = {tree: float('inf') for tree in forest.nodes}
    previous = {tree: None for tree in forest.nodes}
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

        for edge in forest.edges:
            if edge.tree1 == current_tree:
                neighbor = edge.tree2
            elif edge.tree2 == current_tree:
                neighbor = edge.tree1
            else:
                continue
            distance = current_distance + edge.distance
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_tree
                heapq.heappush(priority_queue, (distance, neighbor))

    path = []
    node = end_tree
    while node:
        path.append(node)
        node = previous[node]
    path.reverse()

    return path, distances[end_tree] if end_tree in distances else float('inf')
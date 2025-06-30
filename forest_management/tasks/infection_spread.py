import heapq
from forest_management.core.forest_graph import ForestGraph
from forest_management.core.tree_node import HealthStatus

def simulate_infection_spread(forest: ForestGraph, start_tree, speed=1.0):
    infection_time = {tree: float('inf') for tree in forest.nodes}  # 确保包含所有节点
    heap = []

    heapq.heappush(heap, (0.0, start_tree))
    infection_time[start_tree] = 0.0
    start_tree.health_status = HealthStatus.INFECTED

    while heap:
        current_time, current_node = heapq.heappop(heap)
        
        for edge in forest.edges:
            if edge.tree1 == current_node:
                neighbor = edge.tree2
            elif edge.tree2 == current_node:
                neighbor = edge.tree1
            else:
                continue

            travel_time = edge.distance / speed
            total_time = current_time + travel_time

            if neighbor in infection_time and total_time < infection_time[neighbor]:  # 添加检查
                infection_time[neighbor] = total_time
                neighbor.health_status = HealthStatus.INFECTED
                heapq.heappush(heap, (total_time, neighbor))

    return sorted([(node, round(time, 2)) for node, time in infection_time.items() if time < float('inf')], key=lambda x: x[1])
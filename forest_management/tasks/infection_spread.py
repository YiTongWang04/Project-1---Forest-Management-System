import heapq
from forest_management.core.forest_graph import ForestGraph
from forest_management.core.tree_node import HealthStatus, TreeNode

def simulate_infection_spread(
    forest: ForestGraph, 
    start_tree: TreeNode, 
    speed: float = 1.0
) -> list[tuple[TreeNode, float]]:
    """模拟病害在森林中的传播"""
    # 参数检查
    if not isinstance(forest, ForestGraph):
        raise TypeError("forest参数必须是ForestGraph类型")
    if start_tree is None:
        raise ValueError("起始树不能为空")
    if not isinstance(start_tree, TreeNode):
        raise TypeError("start_tree参数必须是TreeNode类型")
    if speed <= 0:
        raise ValueError("传播速度必须大于0")
    if start_tree not in forest.adjacency:
        raise ValueError("起始树不在森林中")
    if start_tree.health_status == HealthStatus.INFECTED:
        raise ValueError("起始树已经是感染状态")

    # 创建节点ID到节点的映射
    node_map = {tree.tree_id: tree for tree in forest.adjacency}
    infection_time = {tree_id: float('inf') for tree_id in node_map}
    
    # 初始化起始节点
    start_node = node_map[start_tree.tree_id]
    heap = [(0.0, id(start_node), start_node)]
    infection_time[start_node.tree_id] = 0.0
    start_node.health_status = HealthStatus.INFECTED

    while heap:
        current_time, _, current_node = heapq.heappop(heap)
        
        if current_time > infection_time[current_node.tree_id]:
            continue

        for path in forest.adjacency[current_node]:
            neighbor = node_map[path.tree2.tree_id] if path.tree1 == current_node else node_map[path.tree1.tree_id]
            if neighbor.health_status == HealthStatus.INFECTED:
                continue
                
            travel_time = path.distance / speed
            total_time = current_time + travel_time

            if total_time < infection_time[neighbor.tree_id]:
                infection_time[neighbor.tree_id] = total_time
                neighbor.health_status = HealthStatus.INFECTED
                heapq.heappush(heap, (total_time, id(neighbor), neighbor))

    return sorted(
        [(node_map[node_id], round(time, 2)) 
         for node_id, time in infection_time.items() if time < float('inf')],
        key=lambda x: x[1]
    )
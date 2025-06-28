import pandas as pd
from enum import Enum, auto
from collections import defaultdict
import heapq
import matplotlib.pyplot as plt
import unittest
import os
import numpy as np  # 用于增强版可视化
import plotly.graph_objects as go  # 用于交互式可视化

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

    def __hash__(self):
        return hash((self.tree_id, self.species, self.age, self.health_status))

    def __eq__(self, other):
        if not isinstance(other, TreeNode):
            return False
        return (self.tree_id == other.tree_id and 
                self.species == other.species and
                self.age == other.age and
                self.health_status == other.health_status)

    def __repr__(self):
        # 返回树的字符串表示
        return (f"TreeNode(ID={self.tree_id}, Species={self.species}, Age={self.age}, "
                f"Health={self.health_status.name})")

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

    def __hash__(self):
        return hash((self.tree1.tree_id, self.tree2.tree_id))

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

# Task 1: Identifying Conservation Areas
def find_conservation_areas(forest):
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

# Task 2: Infection Spread Simulation
def simulate_infection_spread(forest, start_tree, speed=1.0):
    """
    使用 Dijkstra 算法计算每棵树的最短传播时间。
    返回：[(TreeNode, 时间秒数)]
    """
    import heapq
    infection_time = {tree: float('inf') for tree in forest.nodes}
    heap = []

    heapq.heappush(heap, (0.0, start_tree))  # (time, node)
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

            if total_time < infection_time[neighbor]:
                infection_time[neighbor] = total_time
                neighbor.health_status = HealthStatus.INFECTED
                heapq.heappush(heap, (total_time, neighbor))

    # 返回按感染时间排序的列表
    return sorted([(node, round(time, 2)) for node, time in infection_time.items() if time < float('inf')], key=lambda x: x[1])

# Task 3: Path Finding
def find_shortest_path(forest, start_tree, end_tree):
    distances = {tree: float('inf') for tree in forest.nodes}
    previous = {tree: None for tree in forest.nodes}  # 新增：记录前驱节点
    distances[start_tree] = 0
    priority_queue = [(0, start_tree)]
    visited = set()

    while priority_queue:
        current_distance, current_tree = heapq.heappop(priority_queue)
        if current_tree in visited:
            continue
        visited.add(current_tree)

        if current_tree == end_tree:
            break  # 找到目标节点后提前退出

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
                previous[neighbor] = current_tree  # 记录前驱节点
                heapq.heappush(priority_queue, (distance, neighbor))

    # 回溯构建路径
    path = []
    node = end_tree
    while node:
        path.append(node)
        node = previous[node]
    path.reverse()  # 反转路径顺序

    return path, distances[end_tree] if end_tree in distances else float('inf')

# Task 4: Graphical Interface
def interactive_visualize(forest):
    print(f"准备可视化 - 节点数: {len(forest.nodes)}, 边数: {len(forest.edges)}")
    
    # 创建位置字典，初始使用tree_id和age作为坐标
    pos = {tree: np.array([tree.tree_id, tree.age], dtype=float) for tree in forest.nodes}
    
    # 改进的力导向布局算法
    k = 0.05  # 减小弹簧常数
    repulsion = 100  # 调整排斥力常数
    dt = 0.01  # 减小时间步长
    min_dist = 0.1  # 最小有效距离
    
    for _ in range(300):
        # 计算弹簧力(吸引力)
        spring_forces = {tree: np.zeros(2) for tree in forest.nodes}
        for edge in forest.edges:
            tree1, tree2 = edge.tree1, edge.tree2
            delta = pos[tree2] - pos[tree1]
            dist = np.linalg.norm(delta)
            if dist > min_dist:  # 添加距离检查
                force = k * (dist - edge.distance) * delta / max(dist, min__dist)  # 防止除以0
                spring_forces[tree1] += force
                spring_forces[tree2] -= force
        
        # 计算排斥力(防止节点重叠)
        repulsion_forces = {tree: np.zeros(2) for tree in forest.nodes}
        trees = list(forest.nodes)
        for i, tree1 in enumerate(trees):
            for tree2 in trees[i+1:]:
                delta = pos[tree2] - pos[tree1]
                dist = np.linalg.norm(delta)
                if dist > min_dist:  # 添加距离检查
                    force = repulsion * delta / (max(dist, min_dist)**3)  # 防止除以0
                    repulsion_forces[tree1] -= force
                    repulsion_forces[tree2] += force
        
        # 更新位置
        for tree in forest.nodes:
            total_force = spring_forces[tree] + repulsion_forces[tree]
            pos[tree] += dt * total_force
    
    # 创建图形
    fig = go.Figure()
    
    # 添加边
    for edge in forest.edges:
        fig.add_trace(go.Scatter(
            x=[pos[edge.tree1][0], pos[edge.tree2][0]],
            y=[pos[edge.tree1][1], pos[edge.tree2][1]],
            mode='lines',
            line=dict(width=1, color='gray'),
            hoverinfo='none'
        ))
    
    # 添加节点 - 确保最小间距
    min_dist = 5  # 最小节点间距
    adjusted_pos = {tree: pos[tree].copy() for tree in forest.nodes}
    
    # 调整重叠节点
    trees = list(forest.nodes)
    for i, tree1 in enumerate(trees):
        for tree2 in trees[i+1:]:
            delta = adjusted_pos[tree2] - adjusted_pos[tree1]
            dist = np.linalg.norm(delta)
            if dist < min_dist and dist > 0:
                adjust = (min_dist - dist) * delta / (2 * dist)
                adjusted_pos[tree1] -= adjust
                adjusted_pos[tree2] += adjust
    
    for tree in forest.nodes:
        fig.add_trace(go.Scatter(
            x=[adjusted_pos[tree][0]],
            y=[adjusted_pos[tree][1]],
            mode='markers',
            marker=dict(
                size=max(10, tree.age/2),  # 控制最小节点大小
                color=['green', 'red', 'orange'][tree.health_status.value-1],
                line=dict(width=2, color='DarkSlateGrey')
            ),
            name=f"{tree.species} (ID:{tree.tree_id})",
            hovertext=f"Species: {tree.species}<br>Age: {tree.age}<br>Status: {tree.health_status.name}",
            hoverinfo='text'
        ))
    
    fig.update_layout(
        title='Interactive Forest Visualization (优化布局)',
        xaxis_title='X Coordinate',
        yaxis_title='Y Coordinate',
        showlegend=True
    )
    
    # 修改显示方式
    try:
        import plotly.io as pio
        pio.renderers.default = "browser"  # 尝试在浏览器中打开
        fig.show()
    except Exception as e:
        print(f"可视化错误: {str(e)}")
        # 保存为HTML文件作为备选方案
        fig.write_html("forest_visualization.html")
        print("图表已保存为 forest_visualization.html")

    # 加载数据集函数
def load_forest_data(trees_file_path, paths_file_path):
    forest = ForestGraph()
    # 使用传入的参数路径
    trees_df = pd.read_csv(trees_file_path)
    paths_df = pd.read_csv(paths_file_path)
    
    # 创建树节点
    for index, row in trees_df.iterrows():
        tree_id = row['tree_id']
        species = row['species']
        age = row['age']
        health_status = HealthStatus[row['health_status'].upper().replace(" ", "_")]
        tree = TreeNode(tree_id, species, age, health_status)
        forest.add_tree(tree)

    # 创建路径
    for index, row in paths_df.iterrows():
        tree_id1 = row['tree_1']
        tree_id2 = row['tree_2']
        distance = row['distance']
        tree1 = next((tree for tree in forest.nodes if tree.tree_id == tree_id1), None)
        tree2 = next((tree for tree in forest.nodes if tree.tree_id == tree_id2), None)
        if tree1 and tree2:
            path = TreePath(tree1, tree2, distance)
            forest.add_path(path)

    return forest

# 测试代码（使用 unittest）
class TestForestGraph(unittest.TestCase):
    def setUp(self):
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

class TestConservationAreas(unittest.TestCase):
    def setUp(self):
        self.forest = ForestGraph()
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.AT_RISK)
        self.tree4 = TreeNode(4, "Oak", 20, HealthStatus.HEALTHY)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree4, 15.2)
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_tree(self.tree3)
        self.forest.add_tree(self.tree4)
        self.forest.add_path(self.path1)
        self.forest.add_path(self.path2)

    def test_find_conservation_areas(self):
        areas = find_conservation_areas(self.forest)
        self.assertEqual(len(areas), 1)
        self.assertIn(self.tree1, areas[0])
        self.assertIn(self.tree2, areas[0])
        self.assertIn(self.tree4, areas[0])
        self.assertNotIn(self.tree3, areas[0])

class TestInfectionSpread(unittest.TestCase):
    def setUp(self):
        self.forest = ForestGraph()
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.HEALTHY)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree3, 15.2)
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_tree(self.tree3)
        self.forest.add_path(self.path1)
        self.forest.add_path(self.path2)

    def test_simulate_infection_spread(self):
        simulate_infection_spread(self.forest, self.tree1)
        self.assertEqual(self.tree1.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree2.health_status, HealthStatus.INFECTED)
        self.assertEqual(self.tree3.health_status, HealthStatus.INFECTED)

class TestShortestPath(unittest.TestCase):
    def setUp(self):
        self.forest = ForestGraph()
        self.tree1 = TreeNode(1, "Oak", 50, HealthStatus.HEALTHY)
        self.tree2 = TreeNode(2, "Pine", 30, HealthStatus.HEALTHY)
        self.tree3 = TreeNode(3, "Maple", 40, HealthStatus.HEALTHY)
        self.path1 = TreePath(self.tree1, self.tree2, 10.5)
        self.path2 = TreePath(self.tree2, self.tree3, 15.2)
        self.forest.add_tree(self.tree1)
        self.forest.add_tree(self.tree2)
        self.forest.add_tree(self.tree3)
        self.forest.add_path(self.path1)
        self.forest.add_path(self.path2)

    def test_find_shortest_path(self):
        distance = find_shortest_path(self.forest, self.tree1, self.tree3)
        self.assertAlmostEqual(distance, 25.7)

class TestLoadForestData(unittest.TestCase):
    def test_load_forest_data(self):
        trees_file_path = "forest_management_dataset-trees.csv"
        paths_file_path = "forest_management_dataset-paths.csv"
        
        # 检查文件是否存在
        if not (os.path.exists(trees_file_path) and os.path.exists(paths_file_path)):
            self.skipTest("测试数据文件不存在")
            
        forest = load_forest_data(trees_file_path, paths_file_path)
        self.assertIsNotNone(forest)
        self.assertIsInstance(forest, ForestGraph)

if __name__ == '__main__':
    base_dir = r"D:\python\2024秋小学期\森林\Project-1---Forest-Management-System\project"
    trees_file = os.path.join(base_dir, "forest_management_dataset-trees.csv")
    paths_file = os.path.join(base_dir, "forest_management_dataset-paths.csv")
    
    # 检查文件是否存在
    if not (os.path.exists(trees_file) and os.path.exists(paths_file)):
        print(f"错误：无法找到数据文件，请检查以下路径：")
        print(f"树木文件路径: {trees_file}")
        print(f"路径文件路径: {paths_file}")
    else:
        forest = load_forest_data(trees_file, paths_file)
        interactive_visualize(forest)
    
    # 修改unittest.main()的调用方式
    try:
        unittest.main(exit=False)  # 设置exit=False防止程序退出
    except SystemExit:
        pass  # 捕获SystemExit异常


class TestExtraFeatures(unittest.TestCase):
    def setUp(self):
        self.forest = ForestGraph()
        # 添加测试数据...
        
    def get_health_stats(self):
        """返回森林健康状态统计"""
        stats = {
            'total_trees': len(self.nodes),
            'healthy': sum(1 for t in self.nodes if t.health_status == HealthStatus.HEALTHY),
            'infected': sum(1 for t in self.nodes if t.health_status == HealthStatus.INFECTED),
            'at_risk': sum(1 for t in self.nodes if t.health_status == HealthStatus.AT_RISK)
        }
        stats.update({
            'healthy_percent': stats['healthy']/stats['total_trees']*100 if stats['total_trees'] > 0 else 0,
            'infected_percent': stats['infected']/stats['total_trees']*100 if stats['total_trees'] > 0 else 0,
            'at_risk_percent': stats['at_risk']/stats['total_trees']*100 if stats['total_trees'] > 0 else 0
        })
        return stats

    def get_species_distribution(self):
        """返回树种分布统计"""
        from collections import defaultdict
        species = defaultdict(int)
        for tree in self.nodes:
            species[tree.species] += 1
        return dict(sorted(species.items(), key=lambda x: x[1], reverse=True))

    def get_largest_conservation_area(self):
        """返回最大保护区信息"""
        areas = find_conservation_areas(self)
        if not areas:
            return None
        
        largest = max(areas, key=len)
        species_dist = defaultdict(int)
        for tree in largest:
            species_dist[tree.species] += 1
            
        return {
            'size': len(largest),
            'trees': largest,
            'species_dist': dict(sorted(species_dist.items(), key=lambda x: x[1], reverse=True))
        }

    def get_average_age(self):
        """返回森林平均年龄"""
        if not self.nodes:
            return 0
        return sum(tree.age for tree in self.nodes) / len(self.nodes)
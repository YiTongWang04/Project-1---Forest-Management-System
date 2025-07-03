from collections import defaultdict
from forest_management.core.forest_graph import ForestGraph
from forest_management.tasks.conservation_areas import find_conservation_areas
from forest_management.core.tree_node import HealthStatus, TreeNode

def get_health_stats(forest: ForestGraph) -> dict:
    """获取森林健康状态统计
    
    Args:
        forest: 森林图对象
    
    Returns:
        包含各类健康状态统计的字典
    """
    total = len(forest.adjacency)
    healthy = sum(t.health_status == HealthStatus.HEALTHY for t in forest.adjacency)
    infected = sum(t.health_status == HealthStatus.INFECTED for t in forest.adjacency)
    at_risk = sum(t.health_status == HealthStatus.AT_RISK for t in forest.adjacency)
    
    return {
        'total_trees': total,
        'healthy': healthy,
        'infected': infected,
        'at_risk': at_risk,
        'healthy_percent': healthy / total * 100 if total else 0,
        'infected_percent': infected / total * 100 if total else 0,
        'at_risk_percent': at_risk / total * 100 if total else 0,
    }

def get_species_distribution(forest: ForestGraph) -> dict:
    """获取树种分布统计
    
    Args:
        forest: 森林图对象
    
    Returns:
        按树种数量降序排列的字典
    """
    species_count = defaultdict(int)
    for tree in forest.adjacency:
        species_count[tree.species] += 1
    return dict(sorted(species_count.items(), key=lambda x: x[1], reverse=True))

def get_largest_conservation_area(forest: ForestGraph) -> dict:
    """获取最大健康保护区信息
    
    Args:
        forest: 森林图对象
    
    Returns:
        包含保护区大小、树木列表和树种分布的字典
    """
    areas = find_conservation_areas(forest)
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

def get_average_age(forest: ForestGraph) -> float:
    """计算森林中树木的平均年龄
    
    Args:
        forest: 森林图对象
    
    Returns:
        平均年龄（没有树木时返回0）
    """
    if not forest.adjacency:
        return 0.0
    return sum(tree.age for tree in forest.adjacency) / len(forest.adjacency)
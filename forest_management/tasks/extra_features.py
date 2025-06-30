from collections import defaultdict
from forest_management.core.forest_graph import ForestGraph
from forest_management.tasks.conservation_areas import find_conservation_areas
from project.forest_management.core.tree_node import HealthStatus

def get_health_stats(forest: ForestGraph):
    stats = {
        'total_trees': len(forest.nodes),
        'healthy': sum(1 for t in forest.nodes if t.health_status == HealthStatus.HEALTHY),
        'infected': sum(1 for t in forest.nodes if t.health_status == HealthStatus.INFECTED),
        'at_risk': sum(1 for t in forest.nodes if t.health_status == HealthStatus.AT_RISK)
    }
    stats.update({
        'healthy_percent': stats['healthy']/stats['total_trees']*100 if stats['total_trees'] > 0 else 0,
        'infected_percent': stats['infected']/stats['total_trees']*100 if stats['total_trees'] > 0 else 0,
        'at_risk_percent': stats['at_risk']/stats['total_trees']*100 if stats['total_trees'] > 0 else 0
    })
    return stats

def get_species_distribution(forest: ForestGraph):
    from collections import defaultdict
    species = defaultdict(int)
    for tree in forest.nodes:
        species[tree.species] += 1
    return dict(sorted(species.items(), key=lambda x: x[1], reverse=True))

def get_largest_conservation_area(forest: ForestGraph):
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

def get_average_age(forest: ForestGraph):
    if not forest.nodes:
        return 0
    return sum(tree.age for tree in forest.nodes) / len(forest.nodes)
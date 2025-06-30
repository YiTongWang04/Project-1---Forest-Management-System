import pandas as pd
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus

def load_forest_data(trees_file_path, paths_file_path):
    forest = ForestGraph()
    trees_df = pd.read_csv(trees_file_path)
    paths_df = pd.read_csv(paths_file_path)
    
    for index, row in trees_df.iterrows():
        tree_id = row['tree_id']
        species = row['species']
        age = row['age']
        health_status = HealthStatus[row['health_status'].upper().replace(" ", "_")]
        tree = TreeNode(tree_id, species, age, health_status)
        forest.add_tree(tree)

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
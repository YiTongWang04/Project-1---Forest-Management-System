import pandas as pd
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus

def load_forest_data(tree_file_path, path_file_path):
    forest = ForestGraph()
    
    # 加载树木数据
    try:
        # 加载树木数据
        trees_df = pd.read_csv(tree_file_path)
        for _, row in trees_df.iterrows():
            try:
                # 解析tree_id, species, age, health_status
                health_status_str = str(row['health_status']).upper().replace(" ", "_")
                if health_status_str not in HealthStatus.__members__:
                    raise ValueError(f"Invalid health status value: {row['health_status']}")
                health_status = HealthStatus[health_status_str]
                tree = TreeNode(row['tree_id'], row['species'], row['age'], health_status)
                forest.add_tree(tree)
            except Exception as e:
                raise ValueError(f"Error parsing tree row: {row.to_dict()} - {str(e)}")  # 修改错误信息格式
                
        # 加载路径数据
        paths_df = pd.read_csv(path_file_path)
        for _, row in paths_df.iterrows():
            try:
                tree_id1 = int(row['tree_1'])  # 改为使用tree_1
                tree_id2 = int(row['tree_2'])  # 改为使用tree_2
                distance = float(row['distance'])
                tree1 = next((tree for tree in forest.adjacency if tree.tree_id == tree_id1), None)
                tree2 = next((tree for tree in forest.adjacency if tree.tree_id == tree_id2), None)
                if tree1 is None or tree2 is None:
                    raise ValueError(f"Tree ID {tree_id1 if tree1 is None else tree_id2} not found in forest nodes, skipping path.")
                path = TreePath(tree1, tree2, distance)
                forest.add_path(path)
            except Exception as e:
                raise ValueError(f"Error parsing path row: {row.to_dict()} - {str(e)}")

    except Exception as e:
        raise ValueError(f"Failed to load forest data: {str(e)}")
        
    return forest

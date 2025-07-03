import os
import unittest
from forest_management.utils.data_loader import load_forest_data
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus

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
    unittest.main()
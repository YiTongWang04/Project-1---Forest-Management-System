import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import tempfile
import os
import time
from forest_management.utils.data_loader import load_forest_data
from forest_management.core.tree_node import HealthStatus

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        # 创建临时测试数据
        self.tree_data = pd.DataFrame({
            'tree_id': [1, 2, 3],
            'species': ['Oak', 'Pine', 'Maple'],
            'age': [50, 30, 40],
            'health_status': ['HEALTHY', 'AT_RISK', 'INFECTED']
        })
        
        self.path_data = pd.DataFrame({
            'tree_1': [1, 2],
            'tree_2': [2, 3],
            'distance': [10.5, 15.2]
        })

    def safe_unlink(self, filename):
        """安全删除文件，处理Windows权限问题"""
        try:
            if os.path.exists(filename):
                os.unlink(filename)
        except PermissionError:
            # 在Windows上，文件可能被占用，等待一下再试
            time.sleep(0.1)
            try:
                os.unlink(filename)
            except PermissionError:
                pass  # 忽略删除失败

    def test_successful_data_loading(self):
        """测试成功加载数据"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            self.tree_data.to_csv(f1.name, index=False)
            self.path_data.to_csv(f2.name, index=False)
            
            try:
                forest = load_forest_data(f1.name, f2.name)
                self.assertEqual(len(forest.adjacency), 3)
                
                # 检查树是否正确加载
                trees = list(forest.adjacency.keys())
                tree_ids = [tree.tree_id for tree in trees]
                self.assertIn(1, tree_ids)
                self.assertIn(2, tree_ids)
                self.assertIn(3, tree_ids)
                
                # 检查路径是否正确加载
                path_count = 0
                for edges in forest.adjacency.values():
                    path_count += len(edges)
                self.assertEqual(path_count, 4)  # 每条路径在两个节点中都有记录
                
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

    def test_invalid_health_status(self):
        """测试无效的健康状态"""
        invalid_tree_data = self.tree_data.copy()
        invalid_tree_data.loc[0, 'health_status'] = 'INVALID_STATUS'
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            invalid_tree_data.to_csv(f1.name, index=False)
            self.path_data.to_csv(f2.name, index=False)
            
            try:
                with self.assertRaises(ValueError) as cm:
                    load_forest_data(f1.name, f2.name)
                self.assertIn("Invalid health status value", str(cm.exception))
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

    def test_missing_tree_file(self):
        """测试缺失的树文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            self.path_data.to_csv(f2.name, index=False)
            
            try:
                with self.assertRaises(ValueError):
                    load_forest_data("nonexistent_file.csv", f2.name)
            finally:
                self.safe_unlink(f2.name)

    def test_missing_path_file(self):
        """测试缺失的路径文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1:
            self.tree_data.to_csv(f1.name, index=False)
            
            try:
                with self.assertRaises(ValueError):
                    load_forest_data(f1.name, "nonexistent_file.csv")
            finally:
                self.safe_unlink(f1.name)

    def test_path_with_missing_tree(self):
        """测试路径引用了不存在的树"""
        invalid_path_data = pd.DataFrame({
            'tree_1': [1, 999],  # 999不存在
            'tree_2': [2, 3],
            'distance': [10.5, 15.2]
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            self.tree_data.to_csv(f1.name, index=False)
            invalid_path_data.to_csv(f2.name, index=False)
            
            try:
                with self.assertRaises(ValueError) as cm:
                    load_forest_data(f1.name, f2.name)
                self.assertIn("Tree ID 999 not found", str(cm.exception))
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

    def test_invalid_tree_data_format(self):
        """测试无效的树数据格式"""
        # 创建一个缺少必需列的DataFrame
        invalid_tree_data = pd.DataFrame({
            'tree_id': [1, 2, 3],
            'species': ['Oak', 'Pine', 'Maple'],
            # 缺少age列
            'health_status': ['HEALTHY', 'AT_RISK', 'INFECTED']
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            invalid_tree_data.to_csv(f1.name, index=False)
            # 使用空的路径数据，避免引用不存在的树
            empty_path_data = pd.DataFrame(columns=['tree_1', 'tree_2', 'distance'])
            empty_path_data.to_csv(f2.name, index=False)
            
            try:
                with self.assertRaises(ValueError) as cm:
                    load_forest_data(f1.name, f2.name)
                self.assertIn("Error parsing tree row", str(cm.exception))
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

    def test_invalid_path_data_format(self):
        """测试无效的路径数据格式"""
        invalid_path_data = pd.DataFrame({
            'tree_1': [1, 2],
            'tree_2': [2, 3],
            'distance': ['invalid', 15.2]  # 非数字距离
        })
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            self.tree_data.to_csv(f1.name, index=False)
            invalid_path_data.to_csv(f2.name, index=False)
            
            try:
                with self.assertRaises(ValueError) as cm:
                    load_forest_data(f1.name, f2.name)
                self.assertIn("Error parsing path row", str(cm.exception))
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

    def test_empty_tree_file(self):
        """测试空的树文件"""
        empty_tree_data = pd.DataFrame(columns=['tree_id', 'species', 'age', 'health_status'])
        empty_path_data = pd.DataFrame(columns=['tree_1', 'tree_2', 'distance'])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            empty_tree_data.to_csv(f1.name, index=False)
            empty_path_data.to_csv(f2.name, index=False)
            
            try:
                forest = load_forest_data(f1.name, f2.name)
                self.assertEqual(len(forest.adjacency), 0)
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

    def test_empty_path_file(self):
        """测试空的路径文件"""
        empty_path_data = pd.DataFrame(columns=['tree_1', 'tree_2', 'distance'])
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f2:
            
            self.tree_data.to_csv(f1.name, index=False)
            empty_path_data.to_csv(f2.name, index=False)
            
            try:
                forest = load_forest_data(f1.name, f2.name)
                self.assertEqual(len(forest.adjacency), 3)
                # 检查没有路径
                for edges in forest.adjacency.values():
                    self.assertEqual(len(edges), 0)
            finally:
                self.safe_unlink(f1.name)
                self.safe_unlink(f2.name)

if __name__ == '__main__':
    unittest.main()
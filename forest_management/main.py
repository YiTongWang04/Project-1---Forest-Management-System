import os
import sys

# 添加项目根目录到 sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from forest_management.dashboard.app import app

if __name__ == '__main__':
    app.run(debug=True)
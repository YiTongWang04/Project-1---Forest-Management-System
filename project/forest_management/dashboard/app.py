import dash
from dash import dcc, html
from forest_management.dashboard.layout import layout
from forest_management.dashboard.callbacks import register_callbacks
from forest_management.core.forest_graph import ForestGraph

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    assets_folder='assets'  # 直接指向同级assets文件夹
)
server = app.server

app.layout = layout

# 初始化森林图并注册回调
forest = ForestGraph()
register_callbacks(app, forest)

if __name__ == '__main__':
    app.run(debug=True)
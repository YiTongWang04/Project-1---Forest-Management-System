import dash
from dash import dcc, html
from forest_management.dashboard.layout import layout
from forest_management.dashboard.callbacks import register_callbacks

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    assets_folder='assets'  # 直接指向同级assets文件夹
)
server = app.server

app.layout = layout

register_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True)
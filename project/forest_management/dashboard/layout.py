import dash
from dash import dcc, html

layout = html.Div(style={
    'fontFamily': 'Segoe UI, sans-serif',
    'backgroundColor': '#e8f5e9',
    'padding': '20px'
}, children=[
    html.H2("🌲 Forest Management Interactive Platform", style={
        'textAlign': 'center',
        'color': '#2e7d32',
        'marginBottom': '30px'
    }),

    dcc.Graph(id='forest-graph', figure=None, style={
        'border': '2px solid #a5d6a7',
        'borderRadius': '10px',
        'padding': '10px',
        'backgroundColor': 'white'
    }),

    html.Div([
        # 树节点添加部分
        html.Div([
            html.H4("Add Tree Node"),
            html.Label("Tree ID"), dcc.Input(id='tree-id', type='number', className="input-box"),
            html.Label("Species"), dcc.Input(id='species', value='Oak', type='text', className="input-box"),
            html.Label("Age"), dcc.Input(id='age', value=20, type='number', className="input-box"),
            html.Label("Health Status"),
            dcc.Dropdown(id='status', options=[
                {'label': 'HEALTHY', 'value': 'HEALTHY'},
                {'label': 'INFECTED', 'value': 'INFECTED'},
                {'label': 'AT_RISK', 'value': 'AT_RISK'}
            ], value='HEALTHY'),
            html.Button("Add Tree", id='add-tree-btn', className="button")
        ], className="section"),

        # 添加路径部分
        html.Div([
            html.H4("Add Path"),
            html.Label("Start Tree ID"), dcc.Input(id='start-id', type='number', className="input-box"),
            html.Label("End Tree ID"), dcc.Input(id='end-id', type='number', className="input-box"),
            html.Label("Distance"), dcc.Input(id='distance', type='number', className="input-box"),
            html.Button("Add Path", id='add-path-btn', className="button")
        ], className="section"),

        # 删除部分
        html.Div([
            html.H4("Remove Tree / Path"),
            html.Label("Tree ID"), dcc.Input(id='remove-tree-id', type='number', className="input-box"),
            html.Button("Remove Tree", id='remove-tree-btn', className="button"),
            html.Label("Path Start ID"), dcc.Input(id='del-start-id', type='number', className="input-box"),
            html.Label("Path End ID"), dcc.Input(id='del-end-id', type='number', className="input-box"),
            html.Button("Remove Path", id='remove-path-btn', className="button")
        ], className="section")
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),

    html.Hr(),

    # 其他功能区
    html.Div([
        html.Div([
            html.H4("🦠 Simulate Infection"),
            html.Label("Infection Start ID"), dcc.Input(id='infect-id', type='number', className="input-box"),
            html.Label("Spread Speed (Distance/sec)"), dcc.Input(id='spread-speed', type='number', value=5, min=0.1, className="input-box"),
            html.Button("Start Simulation", id='simulate-btn', className="button")
        ], className="section"),

        html.Div([
            html.H4("📍 Find Shortest Path"),
            html.Label("Start Tree ID"), dcc.Input(id='shortest-start', type='number', className="input-box"),
            html.Label("End Tree ID"), dcc.Input(id='shortest-end', type='number', className="input-box"),
            html.Button("Find Path", id='shortest-btn', className="button")
        ], className="section"),

        html.Div([
            html.H4("🛡️ Identify Conservation Area"),
            html.Button("Highlight Conservation Area", id='conserve-btn', className="button")
        ], className="section"),
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),

    html.Div(id='result-text', style={'whiteSpace': 'pre-wrap', 'marginTop': '20px', 'color': '#1b5e20', 'backgroundColor': '#f1f8e9', 'padding': '10px'}),

    html.Hr(),

    # 功能区布局调整
    html.Div([
        # 第一行：统计图表和数据操作
        html.Div([
            # 统计图表部分，占2/3宽度
            html.Div([
                html.H4("🌳 Forest Health and Species Statistics"),
                # 使用flex布局让两个图横着排列
                html.Div([
                    # 健康状态统计图
                    dcc.Graph(id='health-stats', figure={}, style={'height': '300px', 'flex': '1', 'paddingRight': '10px'}),
                    # 树种统计图
                    dcc.Graph(id='species-stats', figure={}, style={'height': '300px', 'flex': '1', 'paddingLeft': '10px'})
                ], style={'display': 'flex', 'width': '100%', 'gap': '10px'}),
                html.Button("Show Statistics", id='stat-btn', className="button", style={'marginTop': '10px'}),
            ], style={'flex': '2', 'paddingRight': '20px'}),

            # 数据操作部分，占1/3宽度
            html.Div([
                html.H4("📁 Forest Data Operations"),
                html.Div([
                    # 导入部分
                    html.Div([
                        html.Label("Tree Data File Path (.csv):"),
                        dcc.Input(id='tree-csv-path', type='text', placeholder='e.g. D:/data/trees.csv', style={'width': '100%', 'marginBottom': '10px'}, className="input-box"),
                        html.Label("Path Data File Path (.csv):"),
                        dcc.Input(id='path-csv-path', type='text', placeholder='e.g. D:/data/paths.csv', style={'width': '100%', 'marginBottom': '10px'}, className="input-box"),
                        html.Button("Import Data", id='import-csv-btn', className="button"),
                    ], style={'marginBottom': '20px'}),

                    # 导出部分
                    html.Div([
                        html.Button("Export Data", id='export-csv-btn', className="button"),
                    ])
                ], style={'display': 'flex', 'flexDirection': 'column', 'gap': '20px', 'marginTop': '20px'})
            ], style={'flex': '1', 'borderLeft': '1px solid #ccc', 'paddingLeft': '20px'}),
        ], style={'display': 'flex', 'width': '100%', 'marginTop': '20px'}),

        # 第二行：初始状态操作
        html.Div([
            html.H4("💾 Initial State Operations"),
            html.Button("Save as Initial State", id='save-init-btn', className="button", style={'marginRight': '10px'}),
            html.Button("Restore Initial State", id='restore-init-btn', className="button", style={'marginRight': '10px'}),
            html.Button("Clear Forest", id='clear-forest-btn', className="button", style={'backgroundColor': '#c62828', 'color': 'white'}),
        ], className="section", style={'marginTop': '30px', 'display': 'flex', 'justifyContent': 'center', 'gap': '10px'}),
    ], style={'width': '100%'}),

    html.Div(id='action-feedback', style={'color': '#1b5e20', 'margin': '10px'})
])
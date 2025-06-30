import dash
from dash import dcc, html

layout = html.Div([
    html.H2("Forest Management Interactive Platform"),
    dcc.Graph(id='forest-graph', figure=None),

    html.Div([
        html.Div([
            html.H4("Add Tree Node"),
            html.Label("Tree ID"), dcc.Input(id='tree-id', type='number'),
            html.Label("Species"), dcc.Input(id='species', value='Oak', type='text'),
            html.Label("Age"), dcc.Input(id='age', value=20, type='number'),
            html.Label("Health Status"),
            dcc.Dropdown(id='status', options=[
                {'label': 'HEALTHY', 'value': 'HEALTHY'},
                {'label': 'INFECTED', 'value': 'INFECTED'},
                {'label': 'AT_RISK', 'value': 'AT_RISK'}
            ], value='HEALTHY'),
            html.Button("Add Tree", id='add-tree-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("Add Path"),
            html.Label("Start Tree ID"), dcc.Input(id='start-id', type='number'),
            html.Label("End Tree ID"), dcc.Input(id='end-id', type='number'),
            html.Label("Distance"), dcc.Input(id='distance', type='number'),
            html.Button("Add Path", id='add-path-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("Remove Tree / Path"),
            html.Label("Tree ID"), dcc.Input(id='remove-tree-id', type='number'),
            html.Button("Remove Tree", id='remove-tree-btn'),
            html.Label("Path Start ID"), dcc.Input(id='del-start-id', type='number'),
            html.Label("Path End ID"), dcc.Input(id='del-end-id', type='number'),
            html.Button("Remove Path", id='remove-path-btn')
        ], style={'width': '32%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Div([
            html.H4("Simulate Infection"),
            html.Label("Infection Start ID"), dcc.Input(id='infect-id', type='number'),
            html.Label("Spread Speed (Distance/sec)"), dcc.Input(id='spread-speed', type='number', value=5, min=0.1),
            html.Button("Start Simulation", id='simulate-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("Find Shortest Path"),
            html.Label("Start Tree ID"), dcc.Input(id='shortest-start', type='number'),
            html.Label("End Tree ID"), dcc.Input(id='shortest-end', type='number'),
            html.Button("Find Path", id='shortest-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("Identify Conservation Area"),
            html.Button("Highlight Conservation Area", id='conserve-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),
    ]),

    html.Div(id='result-text', style={'whiteSpace': 'pre-wrap', 'marginTop': '20px', 'color': 'blue'}),

    html.Div([
        html.Div([
            html.H4("Forest Health and Species Statistics"),
            html.Button("Show Statistics", id='stat-btn'),
            
            html.Div([
                dcc.Graph(id='health-stats', style={'width': '48%', 'display': 'inline-block'}),
                dcc.Graph(id='species-stats', style={'width': '48%', 'display': 'inline-block'}),
            ])
        ], style={'width': '100%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.H4("Initial State Operations"),
        html.Button("Save as Initial State", id='save-init-btn', style={'marginRight': '10px'}),
        html.Button("Restore Initial State", id='restore-init-btn', style={'marginRight': '10px'}),
        html.Button("Clear Forest", id='clear-forest-btn', style={'backgroundColor': 'red', 'color': 'white'})
    ], style={'margin': '20px 0'}),

    html.Div([
        html.H4("Export Forest Data to CSV"),
        html.Button("Export Data", id='export-csv-btn'),
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '20px'}),
    
    html.Div([
        html.H4("Import Forest Data from CSV"),
        html.Label("Tree Data File Path (.csv):"),
        dcc.Input(id='tree-csv-path', type='text', placeholder='e.g. D:/data/trees.csv', style={'width': '80%'}),
        html.Br(),
        html.Label("Path Data File Path (.csv):"),
        dcc.Input(id='path-csv-path', type='text', placeholder='e.g. D:/data/paths.csv', style={'width': '80%'}),
        html.Br(),
        html.Button("Import Data", id='import-csv-btn'),
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '20px'}),

    html.Div(id='action-feedback', style={'color': 'green', 'margin': '10px'})
])
import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import numpy as np
from uuid import uuid4
import copy  # 用于深拷贝对象
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))  

from forest_module import ForestGraph, TreeNode, TreePath, HealthStatus, simulate_infection_spread, find_conservation_areas, find_shortest_path, load_forest_data

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# 初始化森林
forest = ForestGraph()
positions = {}

# 保存初始状态
initial_forest_state = None

# 工具函数：更新图形
def generate_figure(highlight_nodes=None, path_nodes=None):
    global positions
    pos = {tree: np.array([tree.tree_id * 10, tree.age], dtype=float) for tree in forest.nodes}
    positions = pos

    fig = go.Figure()
    
    # 绘制路径和距离标签
    for edge in forest.edges:
        x0, y0 = pos[edge.tree1]
        x1, y1 = pos[edge.tree2]
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2  # 中点坐标

        # 画线
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color='gray'),
            hoverinfo='none'
        ))

        # 在路径中点添加距离文字
        fig.add_trace(go.Scatter(
            x=[mid_x],
            y=[mid_y],
            mode='text',
            text=[f"{edge.distance:.1f}"],
            textposition="middle center",
            showlegend=False,
            hoverinfo='none',
            textfont=dict(color='black', size=12)
        ))

    # 绘制树节点
    for tree in forest.nodes:
        color = ['green', 'red', 'orange'][tree.health_status.value - 1]
        if highlight_nodes and tree in highlight_nodes:
            color = 'blue'
        if path_nodes and tree in path_nodes:
            color = 'purple'

        fig.add_trace(go.Scatter(
            x=[pos[tree][0]], y=[pos[tree][1]],
            mode='markers+text',
            marker=dict(size=15, color=color),
            text=[f"ID:{tree.tree_id}"], textposition="top center",
            hovertext=f"Species: {tree.species}\nAge: {tree.age}\nStatus: {tree.health_status.name}",
            hoverinfo="text"
        ))
    
    fig.update_layout(title="森林图交互式可视化", showlegend=False)
    return fig

app.layout = html.Div([
    html.H2("森林管理交互平台"),
    dcc.Graph(id='forest-graph', figure=generate_figure()),

    html.Div([
        html.Div([
            html.H4("添加树节点"),
            html.Label("树ID"), dcc.Input(id='tree-id', type='number'),
            html.Label("树种"), dcc.Input(id='species', value='Oak', type='text'),
            html.Label("年龄"), dcc.Input(id='age', value=20, type='number'),
            html.Label("健康状态"),
            dcc.Dropdown(id='status', options=[
                {'label': 'HEALTHY', 'value': 'HEALTHY'},
                {'label': 'INFECTED', 'value': 'INFECTED'},
                {'label': 'AT_RISK', 'value': 'AT_RISK'}
            ], value='HEALTHY'),
            html.Button("添加树", id='add-tree-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("添加路径"),
            html.Label("起点ID"), dcc.Input(id='start-id', type='number'),
            html.Label("终点ID"), dcc.Input(id='end-id', type='number'),
            html.Label("距离"), dcc.Input(id='distance', type='number'),
            html.Button("添加路径", id='add-path-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("删除树/路径"),
            html.Label("树ID"), dcc.Input(id='remove-tree-id', type='number'),
            html.Button("删除树", id='remove-tree-btn'),
            html.Label("路径起点ID"), dcc.Input(id='del-start-id', type='number'),
            html.Label("路径终点ID"), dcc.Input(id='del-end-id', type='number'),
            html.Button("删除路径", id='remove-path-btn')
        ], style={'width': '32%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.Div([
            html.H4("模拟感染"),
            html.Label("感染起点ID"), dcc.Input(id='infect-id', type='number'),
            html.Label("传播速度（距离/秒）"), dcc.Input(id='spread-speed', type='number', value=5, min=0.1),
            html.Button("开始传播", id='simulate-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("寻找最短路径"),
            html.Label("起点ID"), dcc.Input(id='shortest-start', type='number'),
            html.Label("终点ID"), dcc.Input(id='shortest-end', type='number'),
            html.Button("查找路径", id='shortest-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),

        html.Div([
            html.H4("确认保护区"),
            html.Button("显示保护区", id='conserve-btn')
        ], style={'width': '32%', 'display': 'inline-block'}),
    ]),

    # 新增结果显示区域
    html.Div(id='result-text', style={'whiteSpace': 'pre-wrap', 'marginTop': '20px', 'color': 'blue'}),

    html.Div([
        html.Div([
            html.H4("森林健康与树种统计"),
            html.Button("显示统计图", id='stat-btn'),
            
            html.Div([
                dcc.Graph(id='health-stats', style={'width': '48%', 'display': 'inline-block'}),
                dcc.Graph(id='species-stats', style={'width': '48%', 'display': 'inline-block'}),
            ])
        ], style={'width': '100%', 'display': 'inline-block'})
    ]),

    html.Div([
        html.H4("初始状态操作"),
        html.Button("保存为初始状态", id='save-init-btn'),
        html.Button("恢复初始状态", id='restore-init-btn')
    ], style={'margin': '20px 0'}),

    html.Div([
        html.H4("导入CSV数据"),
        html.Label("树数据文件路径 (.csv):"),
        dcc.Input(id='tree-csv-path', type='text', placeholder='例如 D:/data/trees.csv', style={'width': '80%'}),
        html.Br(),
        html.Label("路径数据文件路径 (.csv):"),
        dcc.Input(id='path-csv-path', type='text', placeholder='例如 D:/data/paths.csv', style={'width': '80%'}),
        html.Br(),
        html.Button("导入数据", id='import-csv-btn'),
    ], style={'border': '1px solid #ccc', 'padding': '10px', 'margin': '20px'}),

    html.Div(id='action-feedback', style={'color': 'green', 'margin': '10px'})
])


@app.callback(
    Output('forest-graph', 'figure'),
    Output('action-feedback', 'children'),
    Input('add-tree-btn', 'n_clicks'),
    State('tree-id', 'value'),  # ✅ 新增：接收用户输入的 ID
    State('species', 'value'),
    State('age', 'value'),
    State('status', 'value'),
    prevent_initial_call=True
)
def add_tree(n_clicks, tree_id, species, age, status):
    try:
        if tree_id is None:
            return dash.no_update, "❌ 请提供树的 ID"

        # 检查是否已存在重复 ID
        if any(t.tree_id == tree_id for t in forest.nodes):
            return dash.no_update, f"⚠️ ID {tree_id} 已存在，不能重复添加"

        tree = TreeNode(int(tree_id), species, int(age), HealthStatus[status])
        forest.add_tree(tree)
        return generate_figure(), f"✅ 成功添加树: ID {tree_id}"
    except Exception as e:
        return dash.no_update, f"❌ 添加失败: {str(e)}"


@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('add-path-btn', 'n_clicks'),
    State('start-id', 'value'),
    State('end-id', 'value'),
    State('distance', 'value'),
    prevent_initial_call=True
)
def add_path(n, start_id, end_id, distance):
    try:
        t1 = next(t for t in forest.nodes if t.tree_id == int(start_id))
        t2 = next(t for t in forest.nodes if t.tree_id == int(end_id))
        forest.add_path(TreePath(t1, t2, float(distance)))
        return generate_figure(), f"路径添加成功"
    except Exception as e:
        return dash.no_update, f"添加路径失败: {str(e)}"


@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('remove-tree-btn', 'n_clicks'),
    State('remove-tree-id', 'value'),
    prevent_initial_call=True
)
def remove_tree(n, tree_id):
    try:
        tree = next(t for t in forest.nodes if t.tree_id == int(tree_id))
        forest.remove_tree(tree)
        return generate_figure(), f"已删除树 ID {tree_id}"
    except Exception as e:
        return dash.no_update, f"删除失败: {str(e)}"


@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('remove-path-btn', 'n_clicks'),
    State('del-start-id', 'value'),
    State('del-end-id', 'value'),
    prevent_initial_call=True
)
def remove_path(n, sid, eid):
    try:
        t1 = next(t for t in forest.nodes if t.tree_id == int(sid))
        t2 = next(t for t in forest.nodes if t.tree_id == int(eid))
        path = next(p for p in forest.edges if (p.tree1 == t1 and p.tree2 == t2) or (p.tree1 == t2 and p.tree2 == t1))
        forest.remove_path(path)
        return generate_figure(), "路径已删除"
    except Exception as e:
        return dash.no_update, f"删除路径失败: {str(e)}"


@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Output('result-text', 'children', allow_duplicate=True),
    Input('simulate-btn', 'n_clicks'),
    State('infect-id', 'value'),
    State('spread-speed', 'value'),
    prevent_initial_call=True
)
def simulate_infection(n, infect_id, speed):
    try:
        speed = float(speed or 1.0)
        if speed <= 0:
            return dash.no_update, "❌ 传播速度必须大于0", ""

        start = next(t for t in forest.nodes if t.tree_id == int(infect_id))
        infection_result = simulate_infection_spread(forest, start, speed)

        fig = generate_figure()
        result_lines = [f"感染传播完成，起点ID: {infect_id}\n传播速度: {speed} 距离/秒\n按传播时间排序："]
        for tree, time in infection_result:
            result_lines.append(f"ID{tree.tree_id}，{time}s 感染")

        return fig, "🦠 感染传播完成", "\n".join(result_lines)
    except Exception as e:
        return dash.no_update, f"❌ 传播失败: {str(e)}", ""

@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Output('result-text', 'children', allow_duplicate=True),
    Input('shortest-btn', 'n_clicks'),
    State('shortest-start', 'value'),
    State('shortest-end', 'value'),
    prevent_initial_call=True
)
def show_shortest_path(n, sid, eid):
    try:
        t1 = next(t for t in forest.nodes if t.tree_id == int(sid))
        t2 = next(t for t in forest.nodes if t.tree_id == int(eid))
        path, total_dist = find_shortest_path(forest, t1, t2)

        # 构建结果字符串
        result_lines = [f"最短路径查询:\n起点ID: {sid}\n终点ID: {eid}\n总距离: {total_dist:.2f}\n路径详情："]
        for i in range(len(path) - 1):
            # 找出段距离
            edge = next(e for e in forest.edges if 
                        (e.tree1 == path[i] and e.tree2 == path[i+1]) or 
                        (e.tree1 == path[i+1] and e.tree2 == path[i]))
            result_lines.append(f"从ID{path[i].tree_id}到ID{path[i+1].tree_id} 距离: {edge.distance:.2f}")
        result_text = "\n".join(result_lines)

        fig = generate_figure(path_nodes=set(path))
        return fig, f"最短距离为: {total_dist:.2f}", result_text

    except Exception as e:
        return dash.no_update, f"路径查找失败: {str(e)}", ""

@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Output('result-text', 'children', allow_duplicate=True),
    Input('conserve-btn', 'n_clicks'),
    prevent_initial_call=True
)
def show_conservation(n):
    areas = find_conservation_areas(forest)
    if areas:
        largest = max(areas, key=len)
        fig = generate_figure(highlight_nodes=set(largest))
        result = f"保护区高亮显示:\n保护区树木数量: {len(largest)}\n树木ID列表: {[t.tree_id for t in largest]}"
        return fig, f"已高亮保护区，共 {len(largest)} 棵树", result
    return dash.no_update, "没有找到健康区域", ""


@app.callback(
    Output('health-stats', 'figure'),
    Output('species-stats', 'figure'),
    Input('stat-btn', 'n_clicks'),
    prevent_initial_call=True
)
def show_stats(n):
    total = len(forest.nodes)
    if total == 0:
        return go.Figure(), go.Figure()

    # 健康状态统计
    status_count = {
        'HEALTHY': sum(1 for t in forest.nodes if t.health_status == HealthStatus.HEALTHY),
        'INFECTED': sum(1 for t in forest.nodes if t.health_status == HealthStatus.INFECTED),
        'AT_RISK': sum(1 for t in forest.nodes if t.health_status == HealthStatus.AT_RISK)
    }

    labels = ['HEALTHY', 'AT_RISK', 'INFECTED']
    values = [status_count['HEALTHY'], status_count['AT_RISK'], status_count['INFECTED']]
    colors = ['green', 'yellow', 'red']

    pie_fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,
        marker=dict(colors=colors)
    )])
    pie_fig.update_layout(title="健康状态分布")

    # 树种统计
    species_count = {}
    for tree in forest.nodes:
        species_count[tree.species] = species_count.get(tree.species, 0) + 1

    bar_fig = go.Figure(data=[go.Bar(
        x=list(species_count.keys()),
        y=list(species_count.values()),
        marker_color='lightblue'
    )])
    bar_fig.update_layout(title="树种分布", xaxis_title="树种", yaxis_title="数量")

    return pie_fig, bar_fig


@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('import-csv-btn', 'n_clicks'),
    State('tree-csv-path', 'value'),
    State('path-csv-path', 'value'),
    prevent_initial_call=True
)
def import_csv_data(n_clicks, tree_path, path_path):
    global forest
    try:
        if not tree_path or not path_path:
            return dash.no_update, "❌ 请提供树数据和路径数据文件路径"
        
        tree_path = tree_path.strip().strip('"\'')
        path_path = path_path.strip().strip('"\'')
        
        forest = load_forest_data(tree_path, path_path)
        return generate_figure(), "✅ 数据导入成功，已更新图形"
    except Exception as e:
        return dash.no_update, f"❌ 导入失败: {str(e)}"

# ==== 新增：保存初始状态 ====
@app.callback(
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('save-init-btn', 'n_clicks'),
    prevent_initial_call=True
)
def save_initial_state(n):
    global initial_forest_state
    try:
        initial_forest_state = copy.deepcopy(forest)
        return "✅ 当前森林状态已保存为初始状态"
    except Exception as e:
        return f"❌ 保存失败: {str(e)}"

# ==== 新增：恢复初始状态 ====
@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('restore-init-btn', 'n_clicks'),
    prevent_initial_call=True
)
def restore_initial_state(n):
    global forest, initial_forest_state
    try:
        if initial_forest_state is None:
            return dash.no_update, "⚠️ 尚未保存任何初始状态"
        forest = copy.deepcopy(initial_forest_state)
        return generate_figure(), "🔄 已恢复到初始状态"
    except Exception as e:
        return dash.no_update, f"❌ 恢复失败: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
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
import pandas as pd
import os

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# 初始化森林
forest = ForestGraph()
positions = {}

# 保存初始状态
initial_forest_state = None

# 工具函数：更新图形
def generate_figure(highlight_nodes=None, path_nodes=None, highlight_paths=None):
    global positions
    pos = {tree: np.array([tree.tree_id * 10, tree.age], dtype=float) for tree in forest.nodes}
    positions = pos

    # 计算每个节点的连接度
    degree_map = {tree: 0 for tree in forest.nodes}
    for edge in forest.edges:
        degree_map[edge.tree1] += 1
        degree_map[edge.tree2] += 1

    fig = go.Figure()
    
    # 绘制路径和距离标签
    for edge in forest.edges:
        x0, y0 = pos[edge.tree1]
        x1, y1 = pos[edge.tree2]
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2  # 中点坐标

        # 路径颜色优先级判断：感染 > 最短路径 > 默认
        if highlight_nodes and (edge.tree1 in highlight_nodes and edge.tree2 in highlight_nodes):
            color = 'red'  # 感染路径
        elif highlight_paths and edge in highlight_paths:
            color = 'blue'  # 最短路径边
        else:
            color = 'gray'

        # 路径线
        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color=color, width=3),
            hoverinfo='none'
        ))

        # 中点距离标签
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
            color = 'red'  # 感染节点
        if path_nodes and tree in path_nodes:
            color = 'blue'  # 最短路径节点

        degree = degree_map.get(tree, 0)
        size = 10 + degree * 5  # 基础大小为10，每增加一个连接度+5

        fig.add_trace(go.Scatter(
            x=[pos[tree][0]], y=[pos[tree][1]],
            mode='markers+text',
            marker=dict(size=size, color=color),
            text=[f"ID:{tree.tree_id}"], textposition="top center",
            hovertext=f"Species: {tree.species}\nAge: {tree.age}\nStatus: {tree.health_status.name}\n连接数: {degree}",
            hoverinfo="text"
        ))
    
    fig.update_layout(title="Interactive Forest Graph", showlegend=False)
    return fig

app.layout = html.Div(style={
    'fontFamily': 'Segoe UI, sans-serif',
    'backgroundColor': '#e8f5e9',
    'padding': '20px'
}, children=[
    html.H2("🌲 Forest Management Interactive Platform", style={
        'textAlign': 'center',
        'color': '#2e7d32',
        'marginBottom': '30px'
    }),

    dcc.Graph(id='forest-graph', figure=generate_figure(), style={
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

    html.Div([
        html.Div([
            html.H4("📊 Forest Health and Species Statistics"),
            html.Button("Show Statistics", id='stat-btn', className="button"),
            html.Div([
                dcc.Graph(id='health-stats', style={
                    'flex': '1',
                    'minWidth': '0',
                    'height': '400px'
                }),
                dcc.Graph(id='species-stats', style={
                    'flex': '1',
                    'minWidth': '0',
                    'height': '400px'
                }),
            ], className="stats-graphs-container", style={
                'display': 'flex',
                'gap': '20px',
                'justifyContent': 'space-between',
                'width': '100%'
            })
        ], className="stats-section-container", style={
            'width': '100%',
            'padding': '20px',
            'marginBottom': '20px'
        })
    ], className="section"),

    html.Div([
        html.H4("💾 Initial State Operations"),
        html.Button("Save as Initial State", id='save-init-btn', className="button", style={'marginRight': '10px'}),
        html.Button("Restore Initial State", id='restore-init-btn', className="button", style={'marginRight': '10px'}),
        html.Button("Clear Forest", id='clear-forest-btn', className="button", style={'backgroundColor': '#c62828', 'color': 'white'})
    ], style={'margin': '20px 0'}),

    html.Div([
        html.H4("📁 Export Forest Data to CSV"),
        html.Button("Export Data", id='export-csv-btn', className="button"),
    ], className="section"),

    html.Div([
        html.H4("📁 Import Forest Data from CSV"),
        html.Label("Tree Data File Path (.csv):"),
        dcc.Input(id='tree-csv-path', type='text', placeholder='e.g. D:/data/trees.csv', style={'width': '80%'}, className="input-box"),
        html.Br(),
        html.Label("Path Data File Path (.csv):"),
        dcc.Input(id='path-csv-path', type='text', placeholder='e.g. D:/data/paths.csv', style={'width': '80%'}, className="input-box"),
        html.Br(),
        html.Button("Import Data", id='import-csv-btn', className="button"),
    ], className="section"),

    html.Div(id='action-feedback', style={'color': '#1b5e20', 'margin': '10px'})
])


# 修改回调中的提示信息
@app.callback(
    Output('forest-graph', 'figure'),
    Output('action-feedback', 'children'),
    Input('add-tree-btn', 'n_clicks'),
    State('tree-id', 'value'),
    State('species', 'value'),
    State('age', 'value'),
    State('status', 'value'),
    prevent_initial_call=True
)
def add_tree(n_clicks, tree_id, species, age, status):
    try:
        if tree_id is None:
            return dash.no_update, "❌ Please provide a tree ID"

        if any(t.tree_id == tree_id for t in forest.nodes):
            return dash.no_update, f"⚠️ Tree ID {tree_id} already exists"

        tree = TreeNode(int(tree_id), species, int(age), HealthStatus[status])
        forest.add_tree(tree)
        return generate_figure(), f"✅ Successfully added tree: ID {tree_id}"
    except Exception as e:
        return dash.no_update, f"❌ Failed to add tree: {str(e)}"


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

        # 找出所有被感染的节点和边
        infected_nodes = set(t for t, _ in infection_result)
        infected_edges = set()
        for edge in forest.edges:
            if edge.tree1 in infected_nodes and edge.tree2 in infected_nodes:
                infected_edges.add(edge)

        fig = generate_figure(highlight_nodes=infected_nodes, highlight_paths=infected_edges)
        
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

        # 找出路径上的所有边
        highlight_edges = set()
        for i in range(len(path) - 1):
            for edge in forest.edges:
                if (edge.tree1 == path[i] and edge.tree2 == path[i+1]) or (edge.tree2 == path[i] and edge.tree1 == path[i+1]):
                    highlight_edges.add(edge)
                    break

        fig = generate_figure(path_nodes=set(path), highlight_paths=highlight_edges)
        
        # 构建结果字符串
        result_lines = [f"最短路径查询:\n起点ID: {sid}\n终点ID: {eid}\n总距离: {total_dist:.2f}\n路径详情："]
        for i in range(len(path) - 1):
            t1, t2 = path[i], path[i+1]
            # 找出这对节点之间的唯一一条路径
            for edge in forest.edges:
                if (edge.tree1 == t1 and edge.tree2 == t2) or (edge.tree1 == t2 and edge.tree2 == t1):
                    result_lines.append(f"从ID{t1.tree_id}到ID{t2.tree_id} 距离: {edge.distance:.2f}")
                    break

        return fig, f"最短距离为: {total_dist:.2f}", "\n".join(result_lines)

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


@app.callback(
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('export-csv-btn', 'n_clicks'),
    prevent_initial_call=True
)
def export_csv(n_clicks):
    try:
        export_dir = r"D:\python\2024秋小学期\森林\Project-1---Forest-Management-System\project"
        os.makedirs(export_dir, exist_ok=True)

        # 导出树节点数据
        tree_data = [{
            'tree_id': t.tree_id,
            'species': t.species,
            'age': t.age,
            'health_status': t.health_status.name
        } for t in forest.nodes]
        df_tree = pd.DataFrame(tree_data)
        df_tree.to_csv(os.path.join(export_dir, 'trees_export.csv'), index=False)

        # 导出路径数据
        path_data = [{
            'tree_1': p.tree1.tree_id,
            'tree_2': p.tree2.tree_id,
            'distance': p.distance
        } for p in forest.edges]
        df_path = pd.DataFrame(path_data)
        df_path.to_csv(os.path.join(export_dir, 'paths_export.csv'), index=False)

        return "✅ 森林数据已成功导出到 trees_export.csv 和 paths_export.csv"
    except Exception as e:
        return f"❌ 导出失败: {str(e)}"


@app.callback(
    Output('forest-graph', 'figure', allow_duplicate=True),
    Output('action-feedback', 'children', allow_duplicate=True),
    Input('clear-forest-btn', 'n_clicks'),
    prevent_initial_call=True
)
def clear_forest(n_clicks):
    global forest
    try:
        forest = ForestGraph()  # 重置为新的空图
        return generate_figure(), "✅ 森林已清空"
    except Exception as e:
        return dash.no_update, f"❌ 清空失败: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
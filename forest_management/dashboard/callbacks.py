from dash import Output, Input, State, callback
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus
from forest_management.tasks.infection_spread import simulate_infection_spread
from forest_management.tasks.path_finding import find_shortest_path
from forest_management.tasks.conservation_areas import find_conservation_areas
from forest_management.visualization.interactive_visualize import generate_figure
from forest_management.utils.data_loader import load_forest_data
import copy
import dash
import pandas as pd
import os
import plotly.graph_objects as go
from collections import defaultdict

forest = ForestGraph()
positions = {}
initial_forest_state = None

def register_callbacks(app):
    @callback(
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
            return generate_figure(forest), f"✅ Successfully added tree: ID {tree_id}"
        except Exception as e:
            return dash.no_update, f"❌ Failed to add tree: {str(e)}"

    @callback(
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
            return generate_figure(forest), "路径添加成功"
        except Exception as e:
            return dash.no_update, f"添加路径失败: {str(e)}"

    @callback(
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
            return generate_figure(forest), f"已删除树 ID {tree_id}"
        except Exception as e:
            return dash.no_update, f"删除失败: {str(e)}"

    @callback(
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
            return generate_figure(forest), "路径已删除"
        except Exception as e:
            return dash.no_update, f"删除路径失败: {str(e)}"

    @callback(
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
            
            infected_nodes = set(t for t, _ in infection_result)
            infected_edges = set()
            for edge in forest.edges:
                if edge.tree1 in infected_nodes and edge.tree2 in infected_nodes:
                    infected_edges.add(edge)
            
            fig = generate_figure(forest, highlight_nodes=infected_nodes, highlight_paths=infected_edges)
            
            result_lines = [f"感染传播完成，起点ID: {infect_id}\n传播速度: {speed} 距离/秒\n按传播时间排序："]
            for tree, time in infection_result:
                result_lines.append(f"ID{tree.tree_id}，{time}s 感染")
            
            return fig, "🦠 感染传播完成", "\n".join(result_lines)
        except Exception as e:
            return dash.no_update, f"❌ 传播失败: {str(e)}", ""

    @callback(
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

            highlight_edges = set()
            for i in range(len(path) - 1):
                for edge in forest.edges:
                    if (edge.tree1 == path[i] and edge.tree2 == path[i+1]) or (edge.tree2 == path[i] and edge.tree1 == path[i+1]):
                        highlight_edges.add(edge)
                        break

            fig = generate_figure(forest, path_nodes=set(path), highlight_paths=highlight_edges)
            
            result_lines = [f"最短路径查询:\n起点ID: {sid}\n终点ID: {eid}\n总距离: {total_dist:.2f}\n路径详情："]
            for i in range(len(path) - 1):
                t1, t2 = path[i], path[i+1]
                for edge in forest.edges:
                    if (edge.tree1 == t1 and edge.tree2 == t2) or (edge.tree1 == t2 and edge.tree2 == t1):
                        result_lines.append(f"从ID{t1.tree_id}到ID{t2.tree_id} 距离: {edge.distance:.2f}")
                        break

            return fig, f"最短距离为: {total_dist:.2f}", "\n".join(result_lines)
        except Exception as e:
            return dash.no_update, f"路径查找失败: {str(e)}", ""

    @callback(
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
            fig = generate_figure(forest, highlight_nodes=set(largest))
            result = f"保护区高亮显示:\n保护区树木数量: {len(largest)}\n树木ID列表: {[t.tree_id for t in largest]}"
            return fig, f"已高亮保护区，共 {len(largest)} 棵树", result
        return dash.no_update, "没有找到健康区域", ""

    @callback(
        Output('health-stats', 'figure'),
        Output('species-stats', 'figure'),
        Input('stat-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_stats(n):
        total = len(forest.nodes)
        if total == 0:
            return go.Figure(), go.Figure()

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

        species_count = defaultdict(int)
        for tree in forest.nodes:
            species_count[tree.species] += 1

        bar_fig = go.Figure(data=[go.Bar(
            x=list(species_count.keys()),
            y=list(species_count.values()),
            marker_color='lightblue'
        )])
        bar_fig.update_layout(title="树种分布", xaxis_title="树种", yaxis_title="数量")

        return pie_fig, bar_fig

    @callback(
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
            return generate_figure(forest), "✅ 数据导入成功，已更新图形"
        except Exception as e:
            return dash.no_update, f"❌ 导入失败: {str(e)}"

    @callback(
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

    @callback(
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
            return generate_figure(forest), "🔄 已恢复到初始状态"
        except Exception as e:
            return dash.no_update, f"❌ 恢复失败: {str(e)}"

    @callback(
        Output('action-feedback', 'children', allow_duplicate=True),
        Input('export-csv-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def export_csv(n_clicks):
        try:
            export_dir = r"D:\python\2024秋小学期\森林\Project-1---Forest-Management-System\project"
            os.makedirs(export_dir, exist_ok=True)

            tree_data = [{
                'tree_id': t.tree_id,
                'species': t.species,
                'age': t.age,
                'health_status': t.health_status.name
            } for t in forest.nodes]
            df_tree = pd.DataFrame(tree_data)
            df_tree.to_csv(os.path.join(export_dir, 'trees_export.csv'), index=False)

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

    @callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('action-feedback', 'children', allow_duplicate=True),
        Input('clear-forest-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_forest(n_clicks):
        global forest
        try:
            forest = ForestGraph()
            return generate_figure(forest), "✅ 森林已清空"
        except Exception as e:
            return dash.no_update, f"❌ 清空失败: {str(e)}"
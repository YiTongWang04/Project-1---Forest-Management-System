import dash
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from forest_management.core.forest_graph import ForestGraph, TreeNode, TreePath, HealthStatus
from forest_management.tasks.infection_spread import simulate_infection_spread
from forest_management.tasks.path_finding import find_shortest_path
from forest_management.tasks.conservation_areas import find_conservation_areas
from forest_management.visualization.interactive_visualize import generate_figure
from forest_management.tasks.extra_features import get_health_stats, get_species_distribution
from forest_management.utils.data_loader import load_forest_data
from forest_management.dashboard.utils import save_initial_state, restore_initial_state
import plotly.graph_objs as go

def register_callbacks(app, forest: ForestGraph):
    # 添加树
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Input('add-tree-btn', 'n_clicks'),
        State('tree-id', 'value'),
        State('species', 'value'),
        State('age', 'value'),
        State('status', 'value'),
        prevent_initial_call=True
    )
    def add_tree(n_clicks, tree_id, species, age, status):
        if not n_clicks or not tree_id or not species or not age or not status:
            raise PreventUpdate
        try:
            health_status = HealthStatus[status]
            new_tree = TreeNode(tree_id, species, age, health_status)
            forest.add_tree(new_tree)
        except Exception as e:
            print(f"Error adding tree: {e}")
        fig = generate_figure(forest)
        return fig

    # 删除树
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Input('remove-tree-btn', 'n_clicks'),
        State('remove-tree-id', 'value'),
        prevent_initial_call=True
    )
    def remove_tree(n_clicks, remove_tree_id):
        if not n_clicks or not remove_tree_id:
            raise PreventUpdate
        tree = next((t for t in forest.adjacency if t.tree_id == int(remove_tree_id)), None)
        if tree:
            forest.remove_tree(tree)
        fig = generate_figure(forest)
        return fig

    # 添加路径
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Input('add-path-btn', 'n_clicks'),
        State('start-id', 'value'),
        State('end-id', 'value'),
        State('distance', 'value'),
        prevent_initial_call=True
    )
    def add_path(n_clicks, start_id, end_id, distance):
        if not n_clicks or not start_id or not end_id or not distance:
            raise PreventUpdate
        start_tree = next((t for t in forest.adjacency if t.tree_id == int(start_id)), None)
        end_tree = next((t for t in forest.adjacency if t.tree_id == int(end_id)), None)
        if start_tree and end_tree:
            new_path = TreePath(start_tree, end_tree, float(distance))
            forest.add_path(new_path)
        fig = generate_figure(forest)
        return fig

    # 删除路径
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Input('remove-path-btn', 'n_clicks'),
        State('del-start-id', 'value'),
        State('del-end-id', 'value'),
        prevent_initial_call=True
    )
    def remove_path(n_clicks, del_start_id, del_end_id):
        if not n_clicks or not del_start_id or not del_end_id:
            raise PreventUpdate
        start_tree = next((t for t in forest.adjacency if t.tree_id == int(del_start_id)), None)
        end_tree = next((t for t in forest.adjacency if t.tree_id == int(del_end_id)), None)
        if start_tree and end_tree:
            def find_edge(t1, t2):
                seen = set()
                for edges in forest.adjacency.values():
                    for p in edges:
                        eid = tuple(sorted([p.tree1.tree_id, p.tree2.tree_id]))
                        if eid in seen:
                            continue
                        seen.add(eid)
                        if (p.tree1 == t1 and p.tree2 == t2) or (p.tree1 == t2 and p.tree2 == t1):
                            return p
                raise ValueError("路径不存在")
            path_to_remove = find_edge(start_tree, end_tree)
            if path_to_remove:
                forest.remove_path(path_to_remove)
        fig = generate_figure(forest)
        return fig

    # 感染模拟
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('result-text', 'children', allow_duplicate=True),
        Input('simulate-btn', 'n_clicks'),
        State('infect-id', 'value'),
        State('spread-speed', 'value'),
        prevent_initial_call=True
    )
    def simulate_infection(n_clicks, infect_id, speed):
        if not n_clicks or not infect_id:
            raise PreventUpdate
        try:
            start_tree = next((t for t in forest.adjacency if t.tree_id == int(infect_id)), None)
            if start_tree:
                infected_trees = simulate_infection_spread(forest, start_tree, float(speed))
                if infected_trees:
                    infected_info = [f"ID:{t[0].tree_id} Time:{t[1]:.2f}" for t in infected_trees]
                    feedback = "Infection Results:\n" + "\n".join(infected_info)
                else:
                    feedback = "No trees were infected."
            else:
                feedback = "Invalid starting tree ID."
                infected_trees = []
            fig = generate_figure(forest, highlight_nodes=[t[0] for t in infected_trees], highlight_color='red')
            return fig, feedback
        except Exception as e:
            return dash.no_update, f"Infection simulation error: {e}"

    # 最短路径
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('result-text', 'children', allow_duplicate=True),
        Input('shortest-btn', 'n_clicks'),
        State('shortest-start', 'value'),
        State('shortest-end', 'value'),
        prevent_initial_call=True
    )
    def find_shortest_path_callback(n_clicks, shortest_start, shortest_end):
        if not n_clicks or not shortest_start or not shortest_end:
            raise PreventUpdate
        start_tree = next((t for t in forest.adjacency if t.tree_id == int(shortest_start)), None)
        end_tree = next((t for t in forest.adjacency if t.tree_id == int(shortest_end)), None)
        if start_tree and end_tree:
            path, distance = find_shortest_path(forest, start_tree, end_tree)
            path_ids = [t.tree_id for t in path]
            feedback = f"Shortest path: {path_ids} with distance: {distance:.2f}"
        else:
            feedback = "Invalid tree IDs."
        fig = generate_figure(forest, path_nodes=path)
        return fig, feedback

    # 保护区
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('result-text', 'children', allow_duplicate=True),
        Input('conserve-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def find_conservation_areas_callback(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        areas = find_conservation_areas(forest)
        if areas:
            largest = max(areas, key=len)
            fig = generate_figure(forest, highlight_nodes=largest, highlight_color='#90ee90')
            ids = [tree.tree_id for tree in largest]
            feedback = f"The largest conservation area: {ids}"
            return fig, feedback
        return dash.no_update, "No healthy areas found"

    # 统计图表
    @app.callback(
        Output('health-stats', 'figure'),
        Output('species-stats', 'figure'),
        Input('stat-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def show_stats(n):
        if not n:
            raise PreventUpdate
        stats = get_health_stats(forest)
        species_distribution = get_species_distribution(forest)
        labels = ['HEALTHY', 'AT_RISK', 'INFECTED']
        values = [stats['healthy'], stats['at_risk'], stats['infected']]
        colors = ['green', 'orange', 'red']
        pie_fig = go.Figure(data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors))])
        pie_fig.update_layout(title="Health Status Distribution")
        bar_fig = go.Figure(data=[go.Bar(
            x=list(species_distribution.keys()),
            y=list(species_distribution.values()),
            marker_color='lightblue'
        )])
        bar_fig.update_layout(title="Species Distribution", xaxis_title="Species", yaxis_title="Count")
        return pie_fig, bar_fig

    # 在文件顶部添加全局变量
    initial_forest_state = None

    # 保存初始状态
    @app.callback(
        Output('action-feedback', 'children', allow_duplicate=True),
        Input('save-init-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def save_initial_state_callback(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        global initial_forest_state
        initial_forest_state = save_initial_state(forest)
        return "Initial state saved."

    # 恢复初始状态
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('action-feedback', 'children', allow_duplicate=True),
        Input('restore-init-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def restore_initial_state_callback(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        global initial_forest_state
        if initial_forest_state:
            restore_initial_state(forest, initial_forest_state)
            fig = generate_figure(forest)
            return fig, "Initial state restored."
        return dash.no_update, "No saved state found"

    # 清空森林
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('action-feedback', 'children', allow_duplicate=True),
        Input('clear-forest-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def clear_forest(n_clicks):
        if not n_clicks:
            raise PreventUpdate
        forest.adjacency.clear()
        fig = generate_figure(forest)
        return fig, "Forest cleared."

    # 导入CSV数据
    @app.callback(
        Output('forest-graph', 'figure', allow_duplicate=True),
        Output('action-feedback', 'children', allow_duplicate=True),
        Input('import-csv-btn', 'n_clicks'),
        State('tree-csv-path', 'value'),
        State('path-csv-path', 'value'),
        prevent_initial_call=True
    )
    def import_csv_data(n_clicks, tree_path, path_path):
        if not n_clicks or not tree_path or not path_path:
            raise PreventUpdate
        try:
            tree_path = tree_path.strip().strip('"\'')
            path_path = path_path.strip().strip('"\'')
            forest_new = load_forest_data(tree_path, path_path)
            forest.adjacency.clear()
            forest.adjacency.update(forest_new.adjacency)  # 使用update方法替换内容
            fig = generate_figure(forest)
            return fig, "✅ Data imported successfully, graph updated"
        except Exception as e:
            return dash.no_update, f"❌ Failed to import: {str(e)}"
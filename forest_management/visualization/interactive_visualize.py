import plotly.graph_objects as go
import numpy as np

def generate_figure(forest, highlight_nodes=None, path_nodes=None, highlight_paths=None):
    pos = {tree: np.array([tree.tree_id * 10, tree.age], dtype=float) for tree in forest.nodes}
    degree_map = {tree: 0 for tree in forest.nodes}
    for edge in forest.edges:
        degree_map[edge.tree1] += 1
        degree_map[edge.tree2] += 1

    fig = go.Figure()
    
    for edge in forest.edges:
        x0, y0 = pos[edge.tree1]
        x1, y1 = pos[edge.tree2]
        mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2

        color = 'gray'
        if highlight_nodes and (edge.tree1 in highlight_nodes and edge.tree2 in highlight_nodes):
            color = 'red'
        elif highlight_paths and edge in highlight_paths:
            color = 'blue'

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color=color, width=3),
            hoverinfo='none'
        ))

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

    for tree in forest.nodes:
        color = ['green', 'red', 'orange'][tree.health_status.value - 1]
        if highlight_nodes and tree in highlight_nodes:
            color = 'red'
        if path_nodes and tree in path_nodes:
            color = 'blue'

        degree = degree_map.get(tree, 0)
        size = 10 + degree * 5

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
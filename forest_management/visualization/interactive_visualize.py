import plotly.graph_objects as go
import numpy as np
from forest_management.core.forest_graph import ForestGraph
from forest_management.core.tree_node import TreeNode
from typing import Optional, List

def generate_figure(
    forest: ForestGraph,
    highlight_nodes: Optional[List[TreeNode]] = None,
    path_nodes: Optional[List[TreeNode]] = None,
    highlight_paths: Optional[List] = None,
    highlight_color: str = '#90ee90'  # 新增参数，默认浅绿色
) -> go.Figure:
    """生成交互式森林可视化图表
    
    Args:
        forest: 森林图对象
        highlight_nodes: 需要高亮显示的节点列表
        path_nodes: 路径上的节点列表
        highlight_paths: 需要高亮显示的路径列表
        highlight_color: 高亮节点的颜色 (默认: '#90ee90'浅绿色)
    
    Returns:
        plotly Figure对象
    """
    # 为每棵树分配位置（按tree_id和age生成示例坐标）
    pos = {tree: np.array([tree.tree_id * 10, tree.age], dtype=float) for tree in forest.adjacency}
    
    # 统计连接度（每棵树的边数）
    degree_map = {tree: len(forest.adjacency[tree]) for tree in forest.adjacency}

    fig = go.Figure()

    # ✅ 绘制边（遍历邻接表）
    seen = set()
    for edges in forest.adjacency.values():
        for path in edges:
            eid = tuple(sorted([path.tree1.tree_id, path.tree2.tree_id]))
            if eid in seen:
                continue
            seen.add(eid)
            tree1, tree2 = path.tree1, path.tree2
            x0, y0 = pos[tree1]
            x1, y1 = pos[tree2]
            mid_x, mid_y = (x0 + x1) / 2, (y0 + y1) / 2

            # 设置边颜色
            color = 'gray'
            if highlight_paths and path in highlight_paths:
                color = 'blue'
            elif highlight_nodes and tree1 in highlight_nodes and tree2 in highlight_nodes:
                color = 'red'

            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode='lines',
                line=dict(color=color, width=3),
                hoverinfo='none'
            ))

            # 添加距离标签
            fig.add_trace(go.Scatter(
                x=[mid_x],
                y=[mid_y],
                mode='text',
                text=[f"{path.distance:.1f}"],
                textposition="middle center",
                showlegend=False,
                hoverinfo='none',
                textfont=dict(color='black', size=12)
            ))

    # ✅ 绘制节点
    for tree in forest.adjacency:
        # 设置节点颜色
        color = ['green', 'red', 'orange'][tree.health_status.value - 1]
        if highlight_nodes and tree in highlight_nodes:
            color = highlight_color  # 使用传入的高亮色
        if path_nodes and tree in path_nodes:
            color = 'blue'

        # 设置节点大小和显示信息
        degree = degree_map.get(tree, 0)
        size = 10 + degree * 5

        fig.add_trace(go.Scatter(
            x=[pos[tree][0]], y=[pos[tree][1]],
            mode='markers+text',
            marker=dict(size=size, color=color),
            text=[f"ID:{tree.tree_id}"], 
            textposition="top center",
            hovertext=f"Species: {tree.species}\nAge: {tree.age}\nStatus: {tree.health_status.name}\nDegree: {degree}",
            hoverinfo="text"
        ))

    fig.update_layout(
        title="Interactive Forest Graph",
        showlegend=False,
        hovermode='closest',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

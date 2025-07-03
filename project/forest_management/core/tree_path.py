class TreePath:
    def __init__(self, tree1, tree2, distance):
        if tree1 == tree2:
            raise ValueError("路径不能连接同一棵树")
        if distance <= 0:
            raise ValueError("距离必须大于0")
        self.tree1 = tree1
        self.tree2 = tree2
        self.distance = distance

    def __hash__(self):
        # 无向边，顺序无关
        return hash(frozenset({self.tree1.tree_id, self.tree2.tree_id}))

    def __eq__(self, other):
        if not isinstance(other, TreePath):
            return False
        return (frozenset({self.tree1, self.tree2}) == frozenset({other.tree1, other.tree2})
                and self.distance == other.distance)

    def __repr__(self):
        return (f"TreePath({self.tree1.tree_id} <-> {self.tree2.tree_id}, "
                f"Distance={self.distance})")
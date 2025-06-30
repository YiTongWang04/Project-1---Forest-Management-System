class TreePath:
    def __init__(self, tree1, tree2, distance):
        if tree1 == tree2:
            raise ValueError("路径不能连接同一棵树")
        self.tree1 = tree1
        self.tree2 = tree2
        self.distance = distance

    def __hash__(self):
        return hash((self.tree1.tree_id, self.tree2.tree_id))

    def __repr__(self):
        return (f"TreePath({self.tree1.tree_id} <-> {self.tree2.tree_id}, "
                f"Distance={self.distance})")

    def __eq__(self, other):
        return (self.tree1 == other.tree1 and self.tree2 == other.tree2) or \
               (self.tree1 == other.tree2 and self.tree2 == other.tree1)
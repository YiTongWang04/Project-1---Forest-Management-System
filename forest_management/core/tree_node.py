from enum import Enum

class HealthStatus(Enum):
    HEALTHY = 1
    INFECTED = 2
    AT_RISK = 3

class TreeNode:
    def __init__(self, tree_id, species, age, health_status=HealthStatus.HEALTHY):
        self.tree_id = tree_id
        self.species = species
        self.age = age
        if not isinstance(health_status, HealthStatus):
            raise ValueError("health_status 必须是 HealthStatus 枚举的实例")
        self.health_status = health_status

    def __hash__(self):
        return hash(self.tree_id)

    def __eq__(self, other):
        return isinstance(other, TreeNode) and self.tree_id == other.tree_id

    def __lt__(self, other):
        return self.tree_id < other.tree_id

    def __repr__(self):
        return (f"TreeNode(ID={self.tree_id}, Species={self.species}, "
                f"Age={self.age}, Health={self.health_status.name})")
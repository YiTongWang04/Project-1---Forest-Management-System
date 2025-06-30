from enum import Enum, auto

class HealthStatus(Enum):
    HEALTHY = auto()
    INFECTED = auto()
    AT_RISK = auto()

class TreeNode:
    def __init__(self, tree_id, species, age, health_status):
        self.tree_id = tree_id
        self.species = species
        self.age = age
        if not isinstance(health_status, HealthStatus):
            raise ValueError("health_status 必须是 HealthStatus 枚举的实例")
        self.health_status = health_status

    def __hash__(self):
        return hash((self.tree_id, self.species, self.age, self.health_status))

    def __eq__(self, other):
        if not isinstance(other, TreeNode):
            return False
        return (self.tree_id == other.tree_id and 
                self.species == other.species and
                self.age == other.age and
                self.health_status == other.health_status)

    def __repr__(self):
        return (f"TreeNode(ID={self.tree_id}, Species={self.species}, Age={self.age}, "
                f"Health={self.health_status.name})")

    def __lt__(self, other):
        return self.tree_id < other.tree_id
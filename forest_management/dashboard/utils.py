import copy


def save_initial_state(forest):
    return copy.deepcopy(forest)

def restore_initial_state(forest, initial_state):
    forest.nodes = initial_state.nodes
    forest.edges = initial_state.edges
import copy


def save_initial_state(forest):
    return copy.deepcopy(forest)

def restore_initial_state(forest, initial_state):
    forest.adjacency = initial_state.adjacency
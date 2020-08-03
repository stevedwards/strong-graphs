import copy
import random
from strong_graphs.utils import determine_order
from strong_graphs.data_structure import Network

__all__ = ["map_distances", "map_graph", "mapping_required"]


def count_left_arcs(order):
    n = len(order)
    return sum(1 for u in range(n) if order[u] > order[(u + 1) % n])


def correct_node_position(order, positions, new_position_j):
    """
    Some order 0, 4, 2, 3, 1
         and q ∈ [0, ..., len(order)-1], say 1

    q = 1
    i = 4
    pos_i = 5 - 1 - 4 = 0
    j = 0
    order[1] = 0, order[0] = 4
    pos[0] = 1,   pos[4] = 0 
    return 4, 0, 2, 3, 1
    """
    i = order[new_position_j]
    new_position_i = len(order) - 1 - i
    j = order[new_position_i]
    order[new_position_j] = j
    order[new_position_i] = i
    positions[j] = new_position_j
    positions[i] = new_position_i
    return order, positions


def reorder_nodes(order, x):
    """
    order = some_shuffle([0, 1, 2, 3, 4,..., n-1])
    If arrows are drawn between consecutive numbers, i.e., 0->1, 1->2, 2->3,..., (n-1)->0, 
    x is the number of times the arrow faces from right ro left (<-) with respect to the order
    """
    assert x > count_left_arcs(order)
    assert x < len(order), "Must have at least one non-negative-arc"
    new_order = copy.copy(order)
    positions = {node: pos for pos, node in enumerate(new_order)}
    sample = random.sample(range(len(order)), x + 1)
    for s in sample:
        q = positions[s]
        new_order, positions = correct_node_position(new_order, positions, q)
    return new_order


def create_mapping(order, m_neg):
    new_order = reorder_nodes(order, m_neg)
    mapping = {old: new for old, new in zip(order, new_order)}
    return mapping


def mapping_required(distances, tree_arcs, m, nb_neg_loop_arcs):
    if nb_neg_loop_arcs == 0:
        return None
    order = determine_order(distances)
    n = len(order)
    assert 0 <= nb_neg_loop_arcs < n, "Must have at least one non-negative-arc"
    assert n == len(set(order)), "No duplicates allowed"
    number_of_left_arcs = count_left_arcs(order)
    return (
        create_mapping(order, nb_neg_loop_arcs)
        if nb_neg_loop_arcs > number_of_left_arcs
        else None
    )


def map_distances(distances, mapping):
    return {mapping[node]: distances[node] for node in mapping}


def map_graph(graph, mapping):
    new_graph = Network()
    for node in graph.nodes():
        new_graph.add_node(node)
    for (u, v, w) in graph.arcs():
        new_graph.add_arc(mapping[u], mapping[v], w)
    return new_graph

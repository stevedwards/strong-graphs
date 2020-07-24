import copy
import random
from strong_graphs.utils import determine_order
from strong_graphs.network import Network

__all__ = ["create_mapping", "map_distances", "map_graph", "reorder_nodes"]

def count_left_arcs(order):
    n = len(order)
    return sum(1 for u in range(n) if order[u] > order[(u + 1) % n])


def correct_node_position(order, q):
    i = order[q]  
    new_position_i = len(order) - 1 - i  
    j = order[new_position_i]
    order[q], order[new_position_i] = j, i
    return order


def remapping_required(order, nb_neg_loop_arcs):
    n = len(order)
    assert 0 <= nb_neg_loop_arcs < n, "Must have at least one non-negative-arc"
    assert n == len(set(order)), "No duplicates allowed"
    number_of_left_arcs = count_left_arcs(order)
    return nb_neg_loop_arcs > number_of_left_arcs


def reorder_nodes(order, x):
    """
    order = some_shuffle([0, 1, 2, 3, 4,..., n-1])
    If arrows are drawn between consecutive numbers, i.e., 0->1, 1->2, 2->3,..., (n-1)->0, 
    x is the number of times the arrow faces from right ro left (<-) with respect to the order
    """
    assert x > count_left_arcs(order)
    assert x < len(order), "Must have at least one non-negative-arc"
    new_order = copy.copy(order)
    sample = random.sample(range(len(order)), x + 1)
    for s in sample:
        # TODO update positions as nodes are swapped
        positions = {node: pos for pos, node in enumerate(new_order)}
        q = positions[s]
        correct_node_position(new_order, q)
    return new_order


def create_mapping(distances, n_neg):
    order = determine_order(distances)
    new_order = reorder_nodes(order, n_neg)
    mapping = {old: new for old, new in zip(order, new_order)}
    return mapping


def map_distances(distances, mapping):
    return {mapping[node]: distances[node] for node in mapping}


def map_graph(graph, mapping):
    new_graph = Network()
    for node in graph.nodes():
        new_graph.add_node(node)
    for (u, v, w) in graph.arcs():
        new_graph.add_arc(mapping[u], mapping[v], w)
    return new_graph

from strong_graphs.components.remaining_arcs import determine_order
from strong_graphs.network import Network
import copy
import random


def count_left_arcs(order):
    n = len(order)
    return sum(1 for u in range(n) if order[u] > order[(u + 1) % n])


def correct_node_position(order, q):
    i = order[q]  # 0
    new_position_i = len(order) - 1 - i  # 3
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
    n = len(order)
    assert x > count_left_arcs(order)
    assert x < n, "Must have at least one non-negative-arc"
    new_order = copy.copy(order)
    sample = random.sample(range(n), x + 1)
    for s in sample:
        # TODO update positions as nodes are swapped
        positions = {node: pos for pos, node in enumerate(new_order)}
        q = positions[s]
        correct_node_position(new_order, q)
    return new_order


def create_mapping(distances, n_neg):
    order, _ = determine_order(distances)
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


def gen_remaining_loop_arcs(random_state, graph, distances, number_of_negative_arcs):
    n = graph.number_of_nodes()
    def determine_if_negative(u):
        return distances[u] > distances[(u+1) % n] and number_of_negative_arcs > 0

    order = list(range(n))
    random_state.shuffle(order)
    for u in range(n):
        v = (u + 1) % n
        is_negative = determine_if_negative(u)
        if is_negative:
            number_of_negative_arcs -= 1
        if (u, v) not in graph._arcs.keys():
            yield (u, v, is_negative)

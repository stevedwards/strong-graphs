from strong_graphs.network import Network
import copy
import random


def gen_remaining_loop_arcs(random_state, graph, distances, number_of_negative_arcs):
    n = graph.number_of_nodes()

    def determine_if_negative(u):
        return distances[u] > distances[(u + 1) % n] and number_of_negative_arcs > 0

    order = list(range(n))
    random_state.shuffle(order)
    for u in range(n):
        v = (u + 1) % n
        is_negative = determine_if_negative(u)
        if is_negative:
            number_of_negative_arcs -= 1
        if (u, v) not in graph._arcs.keys():
            yield (u, v, is_negative)

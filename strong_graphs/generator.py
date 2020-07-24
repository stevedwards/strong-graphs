import itertools
import math
import random
from functools import partial
from collections import defaultdict
from strong_graphs.network import Network
from strong_graphs.components.tree import gen_tree_arcs
from strong_graphs.components.remaining_arcs import gen_remaining_arcs, distribute
from strong_graphs.components.loop_arcs import gen_remaining_loop_arcs
from strong_graphs.components.reordering import (
    map_graph,
    map_distances,
    remapping_required,
    reorder_nodes,
    create_mapping,
)
from strong_graphs.draw import draw_graph


__all__ = ["build_instance"]


def determine_arc_signs(random_state, n, m, r):
    arcs_remaining = max((m - 1) - (n - 1), 0)
    nb_neg_arcs = math.floor(arcs_remaining * r)
    nb_neg_loop_arcs = random_state.randint(0, min(nb_neg_arcs, n - 1))  # Determine
    nb_neg_loop_arcs = n - 1
    nb_neg_non_loop_arcs = nb_neg_arcs - nb_neg_loop_arcs
    return nb_neg_loop_arcs, nb_neg_non_loop_arcs


def determine_arc_weight(random_state, D, x, is_negative):
    return random_state.randint(x, 0) if is_negative else D(random_state) + max(x, 0)


def determine_shortest_path_distances(tree):
    """Optimal path found using breadth first search on tree O(n + m), i.e., fast."""
    distances = defaultdict(int)
    queue = set([0])
    while queue:
        u = queue.pop()
        for v, w in tree.successors(u):
            distances[v] = distances[u] + w
            queue.add(v)
    return distances


def build_instance(
    ξ, n, m, r, tree_weight_distribution, D2,
):
    """This can be considered the body of the graph generation algorithm."""
    network = Network(nodes=range(n))
    # Create optimal shortest path tree
    for u, v in gen_tree_arcs(ξ, n, m):
        w = tree_weight_distribution(ξ)
        network.add_arc(u, v, w)  # Note this is the optimal tree
    distances = determine_shortest_path_distances(network)
    # Determine the signs of remaining arc noting that the tree
    # might have to be relabelled for large ratios of negative arcs
    m_neg_loop, m_neg_other = determine_arc_signs(ξ, n, m, r)
    if remapping_required(distances, m_neg_loop):
        mapping = create_mapping(distances, m_neg_loop)
        network = map_graph(network, mapping)
        distances = map_distances(distances, mapping)
    # Add the remaining arcs - first the loop arcs then the remaining arcs
    for (u, v, is_negative) in itertools.chain(
        gen_remaining_loop_arcs(ξ, network, distances, m_neg_loop),
        gen_remaining_arcs(ξ, network, distances, n, m, m_neg_other),
    ):
        δ = distances[v] - distances[u]
        w = determine_arc_weight(ξ, D2, δ, is_negative)
        assert (is_negative and w <= 0) or (not is_negative and w >= 0)
        network.add_arc(u, v, w)
    return network, tree, distances


if __name__ == "__main__":

    random_state = random.Random()
    n = 20
    d = 0.5
    m = int(n * (n - 1) / 2) + 1  # n + math.floor(d * n * (n - 2))
    network, tree, distances = build_instance(
        random_state,
        n=n,
        m=m,
        r=1,
        tree_weight_distribution=partial(random.Random.randint, a=-10000, b=-1),
        D2=partial(random.Random.randint, a=0, b=100),
    )
    draw_graph(network, tree, distances)

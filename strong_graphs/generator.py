import itertools
import math
from collections import defaultdict
from strong_graphs.network import Network
from strong_graphs.network import negative_predecessors
from strong_graphs.components.tree import create_optimal_tree, determine_shortest_path_distances
from strong_graphs.components.remaining_arcs import gen_remaining_arcs, distribute
from strong_graphs.components.loop_arcs import (
    gen_remaining_loop_arcs,
    create_mapping,
    map_distances,
    map_graph,
    remapping_required,
)
import random
from functools import partial
from draw import draw_graph


__all__ = ["build_instance"]

def determine_arc_signs(random_state, n, m, r):
    arcs_remaining = max((m - 1) - (n - 1), 0)
    nb_neg_arcs = math.floor(arcs_remaining * r)
    nb_neg_loop_arcs = random_state.randint(0, min(nb_neg_arcs, n - 1)) # Determine
    nb_neg_loop_arcs = n - 1
    nb_neg_non_loop_arcs = nb_neg_arcs - nb_neg_loop_arcs
    return nb_neg_loop_arcs, nb_neg_non_loop_arcs

def neg_weight(random_state, x):
    return random_state.randint(x, 0)

def pos_weight(random_state, x):
    return random_state.randint(random_state) + max(x, 0)

def build_instance(
    ξ,
    n,
    m,
    r,
    tree_weight_distribution,
    non_tree_weight_distribution,
    arc_distribution,
):
    """This can be considered the body of the graph generation algorithm."""
    network = Network(nodes=range(n))
    # Create optimal shortest path tree
    for u, v in gen_tree_arcs(ξ, n, m):
        w = tree_weight_distribution(ξ)
        network.add_arc(u, v, w)
    distances = determine_shortest_path_distances(network)
    # Next determine the signs of remaining arc noting that the tree
    # might have to be relabelled for large ratios of negative arcs
    nb_neg_loop_arcs, nb_neg_other_arcs = determine_arc_signs(ξ, n, m, r)
    if remapping_required(distances, nb_neg_loop_arcs):
        mapping = create_mapping(distances, nb_neg_loop_arcs)
        network, distances = map_graph(network, mapping), map_distances(distances, mapping)
    # Add the remaining arcs - first the loop arcs then the remaining arcs
    for (u, v, is_negative) in itertools.chain(
        gen_remaining_loop_arcs(ξ, network, distances, nb_neg_loop_arcs),
        gen_remaining_arcs(ξ, network, distances, n, m, nb_neg_other_arcs),
    ):
        δ = distances[v] - distances[u]
        w = neg_weight(ξ, δ) if is_negative else pos_weight(ξ, δ)
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
        non_tree_weight_distribution=partial(random.Random.randint, a=0, b=100),
        arc_distribution=distribute,
    )
    draw_graph(network, tree, distances)

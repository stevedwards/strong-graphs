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
from numpy import nextafter
from strong_graphs.draw import draw_graph
from strong_graphs.utils import determine_alpha_beta


__all__ = ["build_instance"]


def determine_arc_signs(random_state, graph, m, r):
    n = graph.number_of_nodes()
    r = nextafter(r, 0.5)
    arcs_remaining = m - graph.number_of_arcs()
    assert arcs_remaining >= 0
    nb_current_negative_arcs = sum(1 for u, v, w in graph.arcs() if w < 0)
    maximum_negative_arcs = int(n * (n - 1) / 2)
    α, β = determine_alpha_beta(float(r))
    neg_loop_arcs = math.floor(random_state.betavariate(α, β)*(n-1))
    return min(neg_loop_arcs, maximum_negative_arcs, nb_current_negative_arcs)


def determine_arc_weight(ξ, D_remaining, x, is_negative):
    """This will make analysing the distribution a little tricky"""

    if is_negative:
        return -D_remaining(ξ, b=min(-x, D_remaining.keywords["b"]))
    else:
        return D_remaining(ξ) + max(x, 0)


def determine_shortest_path_distances(tree):
    """Optimal path found using breadth first search on tree, O(n + m)"""
    distances = defaultdict(int)
    queue = set([0])
    while queue:
        u = queue.pop()
        for v, w in tree.successors(u):
            distances[v] = distances[u] + w
            queue.add(v)
    return distances


def build_instance(
    ξ, n, m, r, D_tree, D_remaining,
):
    """The graph generation algorithm."""
    assert n <= m <= n * (n - 1), f"invalid number of arcs {m=}"
    source = 0
    network = Network(nodes=range(n))
    # Create optimal shortest path tree
    tree_arcs = set()
    for u, v in gen_tree_arcs(ξ, n, m):
        tree_arcs.add((u, v))
        w = D_tree(ξ)
        network.add_arc(u, v, w)  # Note this is the optimal tree
    distances = determine_shortest_path_distances(network)
    # Determine the signs of remaining arc noting that the tree
    # might have to be relabelled for large ratios of negative arcs
    m_neg_loop = determine_arc_signs(ξ, network, m, r)
    mapping={}
    if remapping_required(distances, m_neg_loop):
        mapping = create_mapping(distances, m_neg_loop)
        source = mapping[source]
        tree_arcs = set((mapping[u], mapping[v]) for (u, v) in tree_arcs)
        network = map_graph(network, mapping)
        distances = map_distances(distances, mapping)
    # Add the remaining arcs - first the loop arcs then the remaining arcs
    for (u, v, is_negative) in itertools.chain(
        gen_remaining_loop_arcs(ξ, network, distances, m_neg_loop),
        gen_remaining_arcs(ξ, network, distances, n, m, r),
    ):
        δ = distances[v] - distances[u]
        w = determine_arc_weight(ξ, D_remaining, δ, is_negative)
        assert (is_negative and w <= 0) or (not is_negative and w >= 0)
        network.add_arc(u, v, w)
    return network, tree_arcs, distances, mapping


if __name__ == "__main__":
    random_state = random.Random()
    n = 20              # Number of nodes
    d = 0.5              # Density
    r = 0.75               # Ratio of negative arcs
    #m = n + math.floor(d * n * (n - 2)) 
    m = int(n*(n-1)/2) + 1
    network, tree_arcs, distances, source = build_instance(
        random_state,
        n=n,
        m=m,
        r=r,
        D_tree=partial(random.Random.randint, a=-1000, b=-1), #-100000, b=-1),
        D_remaining=partial(random.Random.randint, a=0, b=1000),
    )
    draw_graph(network, tree_arcs, distances)

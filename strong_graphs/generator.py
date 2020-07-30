import itertools
import math
import random
from functools import partial
from collections import defaultdict
from strong_graphs.network import Network
from strong_graphs.negative import (
    nb_neg_arcs,
    nb_neg_loop_arcs,
    nb_neg_tree_arcs,
    nb_neg_remaining,
)
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
from strong_graphs.utils import nb_arcs_from_density

__all__ = ["build_instance"]

def arc_weight_tree(ξ, D, is_negative):
    """This will make analysing the distribution a little tricky"""
    if is_negative:
        x = D(ξ, b=min(0, D.keywords["b"]))
        assert x <= 0, f"{x=}"
        return x
    else:
        x = D(ξ, a=max(0, D.keywords["a"]))
        assert x >= 0, f"{x=}"
        return x


def arc_weight_remaining(ξ, D, δ, is_negative):
    """This will make analysing the distribution a little tricky"""
    if is_negative:
        x = D(ξ, a=max(δ, D.keywords["a"]), b=0)
        assert x <= 0, f"{x=}"
        return x
    else:
        x = D(ξ, a=0) + max(δ, 0)
        assert x >= 0, f"{x=}"
        return x


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


def build_instance(ξ, n, m, r, D):
    """The graph generation algorithm."""
    assert n <= m <= n * (n - 1), f"invalid number of arcs {m=}"
    source = 0
    network = Network(nodes=range(n))
    m_neg = nb_neg_arcs(n, m, r)

    # Create optimal shortest path tree
    m_neg_tree = nb_neg_tree_arcs(ξ, n, m, m_neg)
    tree_arcs = set()
    for u, v in gen_tree_arcs(ξ, n, m):
        is_negative = network.number_of_arcs() < m_neg_tree
        w = arc_weight_tree(ξ, D, is_negative)
        tree_arcs.add((u, v))
        network.add_arc(u, v, w)
    distances = determine_shortest_path_distances(network)

    # Determine the number of negative loop arcs
    m_neg_tree_loop = sum(1 for u, v in tree_arcs if v == (u + 1) % n)
    m_neg_loop = nb_neg_loop_arcs(ξ, n, m, m_neg, m_neg_tree, m_neg_tree_loop)
    mapping = {}
    if remapping_required(distances, m_neg_loop):
        mapping = create_mapping(distances, m_neg_loop)
        source = mapping[source]
        tree_arcs = set((mapping[u], mapping[v]) for (u, v) in tree_arcs)
        network = map_graph(network, mapping)
        distances = map_distances(distances, mapping)

    # Add the remaining arcs - first the loop arcs then the remaining arcs
    for (u, v, is_negative) in itertools.chain(
        gen_remaining_loop_arcs(ξ, network, distances, m_neg_loop),
        gen_remaining_arcs(ξ, network, distances, n, m, m_neg),
    ):
        δ = distances[v] - distances[u]
        w = arc_weight_remaining(ξ, D, δ, is_negative)
        assert (is_negative and w <= 0) or (not is_negative and w >= 0)
        network.add_arc(u, v, w)
    return network, tree_arcs, distances, mapping


if __name__ == "__main__":

    random_state = random.Random()
    n = 1  # Number of nodes
    d = 1  # Density
    r = 0.2  # Ratio of negative arcs
    D = partial(random.Random.randint, a=-1000, b=1000)
    m = nb_arcs_from_density(n, d)
    network, tree_arcs, distances, source = build_instance(
        random_state,
        n=n,
        m=m,
        r=r,
        D=D,
    )
    draw_graph(network, tree_arcs, distances)

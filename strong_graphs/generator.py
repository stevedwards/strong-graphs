import itertools
import math
import random
from functools import partial
from collections import defaultdict
from strong_graphs.data_structure import Network
from strong_graphs.negative import (
    nb_neg_arcs,
    nb_neg_loop_arcs,
    nb_neg_tree_arcs,
    nb_neg_remaining,
)
from strong_graphs.arc_generators import (
    gen_tree_arcs,
    gen_remaining_arcs,
    gen_loop_arcs,
)
from strong_graphs.mapping import (
    map_graph,
    map_distances,
    mapping_required,
)
from strong_graphs.visualise.draw import draw_graph
from strong_graphs.utils import (
    nb_arcs_from_density,
    shortest_path,
    nb_arcs_in_complete_dag,
)

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

def nb_current_non_pos_tree_loop(network):
    return sum(1 for u, v, w in network.arcs() if v == (u + 1) and w <= 0)


def build_instance(ξ, n, m, r, D):
    """The graph generation algorithm."""
    assert n <= m <= n * (n - 1), f"invalid number of arcs {m=}"
    network = Network(nodes=range(n))
    # Create optimal shortest path tree
    m_neg = nb_neg_arcs(n, m, r)
    m_neg_tree = nb_neg_tree_arcs(ξ, n, m, m_neg)
    tree_arcs = set()
    for u, v in gen_tree_arcs(ξ, n, m, m_neg_tree):
        is_negative = network.number_of_arcs() < m_neg_tree
        w = arc_weight_tree(ξ, D, is_negative)
        tree_arcs.add((u, v))
        network.add_arc(u, v, w)
    distances = shortest_path(network) 
    m_neg_tree_loop = min(m_neg_tree, nb_current_non_pos_tree_loop(network))
    m_neg_loop = nb_neg_loop_arcs(ξ, n, m, m_neg, m_neg_tree, m_neg_tree_loop)
    # Determine the number of negative loop arcs
    if (mapping := mapping_required(distances, m_neg_loop)):
        tree_arcs = set((mapping[u], mapping[v]) for (u, v) in tree_arcs)
        network = map_graph(network, mapping)
        distances = map_distances(distances, mapping)
        m_neg_loop = min(m_neg_tree, sum(1 for u, v in tree_arcs if v == (u + 1) % n and w <= 0))
    # Add the remaining arcs - first the loop arcs then the remaining arcs
    for (u, v, is_negative) in itertools.chain(
        gen_loop_arcs(ξ, network, distances, m_neg_loop - m_neg_tree_loop),
        gen_remaining_arcs(ξ, network, distances, n, m, m_neg),
    ):
        δ = distances[v] - distances[u]
        w = arc_weight_remaining(ξ, D, δ, is_negative)
        assert (is_negative and w <= 0) or (not is_negative and w >= 0)
        network.add_arc(u, v, w)
    return network, tree_arcs, distances, mapping


if __name__ == "__main__":
    ξ = random.Random(1)
    n = 39  # Number of nodes
    d = 0.0010956253986627031  # Density
    r = 0.1375000000000002  # Ratio of negative arcs
    D = partial(random.Random.randint, a=-11, b=31)
    m = nb_arcs_from_density(n, d)

    network, tree_arcs, distances, source = build_instance(ξ, n=n, m=m, r=r, D=D,)
    draw_graph(network, tree_arcs, distances)

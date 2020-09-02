import itertools
import math
import random
from functools import partial
from strong_graphs.data_structure import Network
from strong_graphs.negative import (
    nb_neg_arcs,
    nb_neg_loop_arcs,
    nb_neg_tree_arcs,
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

    network = Network(nodes=range(n+1))
    # Create optimal shortest path tree
    m_neg = nb_neg_arcs(n, m, r)
    m_neg_tree = nb_neg_tree_arcs(ξ, n, m, m_neg)
    tree_arcs = set()
    source = 0
    for u, v in gen_tree_arcs(ξ, n, m, m_neg_tree):
        is_negative = network.number_of_arcs() < m_neg_tree
        w = arc_weight_tree(ξ, D, is_negative)
        tree_arcs.add((u, v))
        network.add_arc(u, v, w)
    distances = shortest_path(network) 
    m_neg_tree_loop = min(m_neg_tree, nb_current_non_pos_tree_loop(network))
    m_neg_loop = nb_neg_loop_arcs(ξ, n, m, m_neg, m_neg_tree, m_neg_tree_loop)
    if (mapping := mapping_required(ξ, distances, m_neg_loop)):
        print("Remapping")
        tree_arcs = set((mapping[u], mapping[v]) for (u, v) in tree_arcs)
        network = map_graph(network, mapping)
        distances = map_distances(distances, mapping)
        source = mapping[source]
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
    return network, tree_arcs, distances, mapping, source
 
def determine_n_and_m(x, d):
    # Determine the number of nodes (n) and arcs (m) from a constant x = (n)(m) and d
    assert 0 <= d <= 1
    assert x >= 1

    n = math.floor(x ** (1 / (2 + d)))
    m = min(x / n, n*(n-1))
    return round(n), round(m)

def determine_n(m, d):
    assert m >= 0
    assert 0 <= d <= 1

    return math.ceil(m ** (1 / (1 + d)))

def change_source_nodes(ξ, network, z):
    n = network.number_of_nodes()
    assert 1 <= z <= n
    network.add_node(-1)
    source_nodes = ξ.sample(range(n), z)
    for node in source_nodes:
        network.add_arc(-1, node, 0)
    

if __name__ == "__main__":

    #m = 100
    ξ = random.Random(0)
    #d = ξ.random()
    #n, m = determine_n_and_m(x, d)
    d = 0
    n = 10 #determine_n(m, d)
    #m = 10000

    #r = ξ.random()
    r = 0.001
    z = ξ.randint(1, n)
    lb = ξ.randint(-10000, 0)
    ub = ξ.randint(0, 10000)
    D = partial(random.Random.randint, a=lb, b=ub)

    m = nb_arcs_from_density(n, d)
    network, tree_arcs, distances, mapping, source = build_instance(ξ, n=n, m=m, r=r, D=D)
    change_source_nodes(ξ, network, z)
    print('complete')
    #draw_graph(network, tree_arcs, distances)
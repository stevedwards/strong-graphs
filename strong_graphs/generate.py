# Project imports
from strong_graphs.data_structures.networks import Network, to_networkx
from strong_graphs.data_structures.trees import DoublyLinkedTree
from strong_graphs.draw import draw_graph

# Other
from math import ceil, floor
import random
import numpy.random as numpy_random
from collections import defaultdict
import itertools
import networkx as nx
import math


def random_choice(my_set):
    return random.sample(my_set, 1)[0]


def create_optimal_tree(n, m):
    tree = DoublyLinkedTree([0])
    # Sample the minimum required loop arcs if necessary
    x = max(0, 2 * n - 1 - m)
    U = set(random.sample(range(n-1), x))
    V = set(range(1, n))-set([u+1 for u in U])

    def dive(u):
        while u in U:
            tree.add(u, u+1)
            u += 1
    # Source node must have at least one successors
    if 0 not in U:
        v = random_choice(V)
        V.remove(v)
        tree.add(0, v)
        dive(v)
    else:
        dive(0)
    # Remaining nodes must have exactly one predecessor
    V = list(V)
    random.shuffle(V)
    for v in V:
        nodes = tree.nodes()
        u = random_choice(nodes)
        tree.add(u, v)
        dive(v)
    return tree


def generate_shortest_path_tree_arcs(n, m):
    # Sample the minimum required loop arcs if necessary
    x = max(0, 2 * n - 1 - m)
    tree_loop_predecessors = set(random.sample(range(n - 1), x))
    for u in tree_loop_predecessors:
        yield (u, u + 1)
    # Sample the remaining arcs
    in_tree = set([v + 1 for v in tree_loop_predecessors])
    incomplete = set(range(n - 1)) - tree_loop_predecessors
    for _ in range(n - 1 - x):
        u = random_choice(in_tree)
        v = incomplete.pop()
        in_tree.add(v)
        yield (u, v)


def determine_shortest_path_distances(network):
    distances = defaultdict(int)
    queue = set([0])
    while queue:
        u = queue.pop()
        for v, w in network.successors(u, with_weight=True):
            distances[v] = distances[u] + w
            queue.add(v)
    return distances


def gen_loop_arcs(graph):
    for u in range(graph.number_of_nodes()):
        v = (u + 1) % n
        if (u, v) not in graph._arcs.keys():
            yield (u, v)


def non_loop_tree_arc(graph, n, v):
    for u in graph.predecessors(v):
        if u != (v - 1) % n:
            return (u, v)
    else:
        return None


def distribute_remaining_arcs_randomly(current_quantity, remaining_quantity, max):
    allocation = defaultdict(int)
    for _ in range(remaining_quantity):
        select_node = random_choice(current_quantity.keys())
        current_quantity[select_node] += 1
        allocation[select_node] += 1
        if current_quantity[select_node] == max:
            current_quantity.pop(select_node)
    return allocation


def gen_remaining_arcs(graph, m, allocation_method):
    """When a graph only consists of a cycle and the optimal shortest path tree, a useful feature is that
    all nodes have at least 1 and at most 2 predecessors."""

    remaining_arcs = m - graph.number_of_arcs()
    # Can do this evenly or randomly
    allocated = allocation_method(
        {node: len(graph._predecessors[node]) for node in graph.nodes()},
        remaining_arcs,
        n - 1,
    )
    for v, a in allocated.items():
        tree_arc = non_loop_tree_arc(graph, n, v)
        q = min(n - 2, a + 1)
        samples = random.sample(
            range(n - 2), q
        )  # Sample one more than required incase it is the tree arc
        count = 0
        for sample in samples:
            u = (v - 2 - sample) % n
            if (u, v) != tree_arc:
                count += 1
                yield (u, v)
            if count == allocated[v]:
                break


def build_instance(
    n,
    m,
    tree_weight_distribution,
    non_tree_weight_distribution,
    arc_distribution,
    ensure_non_negative,
):
    random
    nodes = range(n)
    network = Network()
    # Add nodes
    for i in nodes:
        network.add_node(i)
    # Add shortest path tree arcs
    solution_tree = create_optimal_tree(n, m)
    for v in range(1, n):
        u = solution_tree._parent[v]
        w = tree_weight_distribution()
        network.add_arc(u, v, w)
    # Determine shortest path distances
    distances = determine_shortest_path_distances(network)
    # Add the remaining arcs ensuring the cycle is built
    for (u, v) in itertools.chain(
        gen_loop_arcs(network), gen_remaining_arcs(network, m, arc_distribution)
    ):
        min_distance = distances[v] - distances[u]
        if ensure_non_negative:
            min_distance = max(min_distance, 0)
        w = non_tree_weight_distribution() + min_distance
        network.add_arc(u, v, w)
    return network, solution_tree, distances


if __name__ == "__main__":
    #random.seed(1)
    n = 24
    d = 0.2
    m = n + floor(d * n * (n - 2))
    print(f"{n=}, {d=}, {m=}")
    D1 = lambda: random.randint(-100, 0)
    D2 = lambda: random.randint(0, 10)  # Must be non-negative
    D3 = distribute_remaining_arcs_randomly
    instance, tree, distances = build_instance(
        n,
        m,
        tree_weight_distribution=D1,
        non_tree_weight_distribution=D2,
        arc_distribution=D3,
        ensure_non_negative=False,
    )

    draw_graph(instance, tree, distances)

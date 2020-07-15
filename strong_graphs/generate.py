
import random
import numpy.random as numpy_random
import itertools
import networkx as nx
import math
from collections import defaultdict
from math import ceil, floor
from strong_graphs.data_structures.networks import SimpleNetwork, Network, to_networkx
from strong_graphs.data_structures.trees import DoublyLinkedTree
from strong_graphs.draw import draw_graph


def random_choice(my_set):
    """Randomly chooses a single element from a set. Probably a better way to do this."""
    assert my_set is not None, "My set is empty"
    print(my_set)
    return random.sample(my_set, 1)[0]


def create_optimal_tree(n, m):
    """Creating the optimal shortest path tree from node 0 to all remaining arcs for a given number
    of nodes (n) and arcs (m).

    At first it may seem superfluous that the optimal tree requires 'm' as an input, as a tree is 
    known to have exactly n-1 arcs. However given that the final graph must also contain a loop containing all of
    the nodes, for small values of m, some care must be taken when building the optimal tree to ensure that
    there are sufficient arcs remaining to build a loop.

    To address this, we first calculate the minimum number of arcs of the optimal tree that are also arcs in 
    the loop, (not including arc (n-1)->(0)). We will refer to these arcs as 'loop arcs'. We sample the
    required number of loop arcs by selecting predecessors from the range 0..(n-2). Note that the loop arcs are
    not yet added to the tree.

    To build the tree we use the following properties. For any tree with at least two nodes,
    - the root node has at least one child
    - all other nodes have exactly one parent. 
    """
    assert m > n-1, "Number of arcs must be able to form a tree"

    # Sample the minimum required loop arcs
    nb_loop_arcs = max(0, 2 * n - 1 - m)
    loop_arc_predecessors = set(random.sample(range(n - 1), nb_loop_arcs))

    def dive(u):
        """Add loop arcs to tree where possible"""
        while u in loop_arc_predecessors:
            tree.add_arc(u, u + 1)
            u += 1

    tree = Network([0])   
    for i in range(n):
        tree.add_node(i)
    # Keep track of nodes without parents in the tree or in the loop arcs. We ignore
    # loop arcs as they will be added by diving when the predecessor is added.
    parentless = set(range(1, n)) - set([u + 1 for u in loop_arc_predecessors])
    # Source node must have at least one child, choose from parentless nodes
    if 0 not in loop_arc_predecessors:
        v = random_choice(parentless)
        parentless.remove(v)
        tree.add_arc(0, v)
        dive(v)
    else:
        dive(0)
    # Remaining nodes must have exactly one parent, choose from nodes in tree.
    parentless = list(parentless)
    random.shuffle(parentless)
    for v in parentless:
        tree_nodes = list(tree.nodes())
        u = random_choice(tree_nodes)
        tree.add_arc(u, v)
        dive(v)
    return tree

def determine_shortest_path_distances(tree):
    """Optimal path found using breadth first search on tree O(n + m), i.e., fast."""
    distances = defaultdict(int)
    queue = set([0])
    while queue:
        u = queue.pop()
        for v, w in tree.successors(u, with_weight=True):
            distances[v] = distances[u] + w
            queue.add(v)
    return distances


def gen_loop_arcs(graph, n):
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
    """A method to distribute the remaining arcs across the nodes. It is intended to have
    an alternative ways to distribute the arcs."""
    allocation = defaultdict(int)
    for _ in range(remaining_quantity):
        select_node = random_choice(current_quantity.keys())
        current_quantity[select_node] += 1
        allocation[select_node] += 1
        if current_quantity[select_node] == max:
            current_quantity.pop(select_node)
    return allocation


def gen_remaining_arcs(graph, n, m, allocation_method):
    """The remaining arcs consist of the arcs in the graph that are not on the main loop or in the
    optimal shortest path tree"""
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
    """This can be considered the body of the graph generation algorithm."""
    nodes = range(n)
    network = Network()
    # Add nodes
    for i in nodes:
        network.add_node(i)
    # Add shortest path tree arcs
    solution_tree = create_optimal_tree(n, m)
    for u, v, _ in solution_tree.arcs():
        w = tree_weight_distribution()
        network.add_arc(u, v, w)
    # Determine shortest path distances
    distances = determine_shortest_path_distances(solution_tree)
    # Add the remaining arcs ensuring the cycle is built
    for (u, v) in itertools.chain(
        gen_loop_arcs(network, n), gen_remaining_arcs(network, n, m, arc_distribution)
    ):
        min_distance = distances[v] - distances[u]
        if ensure_non_negative:
            min_distance = max(min_distance, 0)
        w = non_tree_weight_distribution() + min_distance
        network.add_arc(u, v, w)
    return network, solution_tree, distances


if __name__ == "__main__":
    # random.seed(1)
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

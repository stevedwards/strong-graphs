import itertools
import math
from collections import defaultdict
from strong_graphs.network import Network
from strong_graphs.network import negative_predecessors
from strong_graphs.remaining_arcs import gen_remaining_arcs, distribute

def create_optimal_tree(random_state, n, m):
    """Creating the optimal shortest path tree from node 0 to all remaining arcs for a given number
    of nodes (n) and arcs (m).

    At first it may seem superfluous that the optimal tree requires 'm' as an input, as a tree is 
    known to have exactly n-1 arcs. However given that the final graph must also contain a loop containing all of
    the nodes, for small values of m (explicitly m < 2n-1), some care must be taken when building the optimal tree to ensure that
    there are sufficient arcs remaining to build a loop.

    To address this, we first calculate the minimum number of arcs of the optimal tree that are also arcs in 
    the loop, (not including arc (n-1)->(0)). We will refer to these arcs as 'loop arcs'. We sample the
    required number of loop arcs by selecting predecessors from the range 0..(n-2). Note that the loop arcs are
    not yet added to the tree.

    To build the tree we use the following properties. For any tree with at least two nodes,
    - the root node has at least one child
    - all other nodes have exactly one parent. 
    """
    assert m > n - 1, "Number of arcs must be able to form a tree"
    # Sample the minimum required loop arcs
    nb_loop_arcs = max(0, 2 * n - 1 - m)
    loop_arc_predecessors = set(random_state.sample(range(n - 1), nb_loop_arcs))
    tree = Network()
    tree.add_node(0)

    def dive(u):
        """Add loop arcs to tree where possible"""
        while u in loop_arc_predecessors:
            tree.add_node(u + 1)
            tree.add_arc(u, u + 1)
            u += 1

    # Keep track of nodes without parents in the tree or in the loop arcs. We ignore
    # loop arcs as they will be added by diving when the predecessor is added.
    parentless = set(range(1, n)) - set([u + 1 for u in loop_arc_predecessors])
    # Source node must have at least one child, choose from parentless nodes
    if 0 not in loop_arc_predecessors:
        v = random_state.choice(list(parentless))
        parentless.remove(v)
        tree.add_node(v)
        tree.add_arc(0, v)
        dive(v)
    else:
        dive(0)
    # Remaining nodes must have exactly one parent, choose from nodes in tree.
    parentless = list(parentless)
    random_state.shuffle(parentless)
    for v in parentless:
        tree_nodes = list(tree.nodes())
        u = random_state.choice(tree_nodes)
        tree.add_node(v)
        tree.add_arc(u, v)
        dive(v)
    return tree


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


def gen_remaining_loop_arcs(graph):
    """Pretty self explanatory. Assumes the optimal tree arcs are already added but will
    work correctly regardless."""
    for u in range(n := graph.number_of_nodes()):
        v = (u + 1) % n
        if (u, v) not in graph._arcs.keys():
            yield (u, v)

def build_instance(
    random_state,
    n,
    m,
    r,
    tree_weight_distribution,
    non_tree_weight_distribution,
    arc_distribution,
    ensure_non_negative,
):
    """This can be considered the body of the graph generation algorithm."""
    network = Network()
    for i in range(n):
        network.add_node(i)
    solution_tree = create_optimal_tree(random_state, n, m)
    for u, v, _ in solution_tree.arcs():
        w = tree_weight_distribution(random_state)
        network.add_arc(u, v, w)
    distances = determine_shortest_path_distances(network)
    # Add loop arcs - TODO rearrange order to ensure minimum arcs are made
    for (u, v) in gen_remaining_loop_arcs(network):
        min_distance = distances[v] - distances[u]
        w = non_tree_weight_distribution(random_state) + min_distance
        network.add_arc(u, v, w)
    # Add remaining arcs explicitly controlling number of negative and positive arc weights
    for (u, v, is_negative) in gen_remaining_arcs(random_state, network, distances, n, m, r):
        min_distance = distances[v] - distances[u]
        if is_negative:
            w = -1
        else:
            w = 1
        network.add_arc(u, v, w)
    return network, solution_tree, distances


if __name__ == "__main__":
    import random
    from functools import partial
    from draw import draw_graph

    random_state = random.Random(0)
    network, tree, distances = build_instance(
        random_state,
        n=20,
        m=380,
        r=1,
        tree_weight_distribution=partial(random.Random.randint, a=-100, b=-1),
        non_tree_weight_distribution=partial(random.Random.randint, a=0, b=100),
        arc_distribution=distribute,
        ensure_non_negative=False
    )
    draw_graph(network, tree, distances)

        
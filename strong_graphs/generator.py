import itertools
from collections import defaultdict
from .network import Network


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


def distribute_remaining_arcs_randomly(
    random_state, current_quantity, remaining_quantity, max
):
    """A method to distribute the remaining arcs across the nodes. It is intended to have
    an alternative ways to distribute the arcs."""
    allocation = defaultdict(int)
    for _ in range(remaining_quantity):
        select_node = random_state.choice(list(current_quantity.keys()))
        current_quantity[select_node] += 1
        allocation[select_node] += 1
        if current_quantity[select_node] == max:
            current_quantity.pop(select_node)
    return allocation


def gen_remaining_arcs(
    random_state, graph, n, m, allocation_method=distribute_remaining_arcs_randomly
):
    """The remaining arcs consist of the arcs in the graph that are not on the main loop or in the
    optimal shortest path tree. Here we use the fact that after the cycle arcs and decision trees are
    added the number of predecessors of each node is at most 2. 

    The remaining arcs are first allocated amongst the nodes according to an 'allocation_method'. Currently
    we just randomly distribute the remaining arcs ensuring that the maximum number of n-1 is not exceeded. 

    Once they are allocated, for each node except the root we sample the allocated number (plus 1) of 
    predecessors randomly. The extra predecessor sampled is in case the node's predecessor in the optimal tree
    is sampled, in which case it is ignored. 
    """
    remaining_arcs = m - graph.number_of_arcs()
    # Allocates arcs to nodes based on the method selected.
    allocated = allocation_method(
        random_state,
        {node: len(graph._predecessors[node]) for node in graph.nodes()},
        remaining_arcs,
        n - 1,
    )

    def non_loop_tree_arc(v):
        """Finds the predecessor is isn't the loop arc if one exists. Note that here there
        is at most two predecessors so this should be quick."""
        for u, _ in graph.predecessors(v):
            if u != (v - 1) % n:
                return (u, v)
        return None

    for v, allocation in allocated.items():
        # Sample one more than required incase it is the tree arc
        q = min(n - 2, allocation + 1)
        samples = random_state.sample(range(n - 2), q)
        count = 0
        tree_arc = non_loop_tree_arc(v)
        for sample in samples:
            u = (
                v - 2 - sample
            ) % n  # We know that the loop arc already exists so this is ignored.
            if (u, v) != tree_arc:
                count += 1
                yield (u, v)
            if count == allocated[v]:
                break


def build_instance(
    random_state,
    n,
    m,
    tree_weight_distribution,
    non_tree_weight_distribution,
    arc_distribution,
    ensure_non_negative,
):
    """This can be considered the body of the graph generation algorithm."""
    network = Network()
    # Add nodes
    for i in range(n):
        network.add_node(i)
    # Add shortest path tree arcs
    solution_tree = create_optimal_tree(random_state, n, m)
    for u, v, _ in solution_tree.arcs():
        w = tree_weight_distribution(random_state)
        network.add_arc(u, v, w)
    # Determine shortest path distances
    distances = determine_shortest_path_distances(network)
    # Add the remaining arcs, first ensuring the cycle is built
    for (u, v) in itertools.chain(
        gen_remaining_loop_arcs(network),
        gen_remaining_arcs(random_state, network, n, m, arc_distribution),
    ):
        min_distance = distances[v] - distances[u]
        if ensure_non_negative:
            min_distance = max(min_distance, 0)
        w = non_tree_weight_distribution(random_state) + min_distance
        network.add_arc(u, v, w)
    return network, solution_tree, distances

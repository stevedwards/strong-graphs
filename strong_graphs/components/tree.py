from strong_graphs.network import Network
from collections import defaultdict

def gen_tree_arcs(random_state, n, m):
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
    tree_nodes = set([0])

    def dive(u):
        """Add loop arcs to tree where possible"""
        while u in loop_arc_predecessors:
            tree_nodes.add(u + 1)
            yield (u, u+1)
            u += 1

    # Keep track of nodes without parents in the tree or in the loop arcs. We ignore
    # loop arcs as they will be added by diving when the predecessor is added.
    parentless = set(range(1, n)) - set([u + 1 for u in loop_arc_predecessors])
    # Source node must have at least one child, choose from parentless nodes
    if 0 not in loop_arc_predecessors:
        v = random_state.choice(list(parentless))
        parentless.remove(v)
        yield (0, v)
        dive(v)
    else:
        yield from dive(0)
    # Remaining nodes must have exactly one parent, choose from nodes in tree.
    parentless = list(parentless)
    random_state.shuffle(parentless)
    for v in parentless:
        tree_nodes_list = list(tree_nodes)
        u = random_state.choice(tree_nodes_list)
        tree_nodes.add(v)
        yield u, v
        dive(v)



import math
from collections import defaultdict, OrderedDict
from strong_graphs.utils import distribute, determine_order
from strong_graphs.negative import nb_neg_remaining
from typing import Dict, Hashable, List
from progress.bar import Bar

__all__ = ["gen_tree_arcs", "gen_loop_arcs", "gen_remaining_arcs"]


def gen_tree_arcs(ξ, n, m, m_neg):
    assert m > n - 1, "Number of arcs must be able to form a tree"
    # Sample the minimum required loop arcs
    nb_loop_arcs = max(0, 2 * n - 1 - m)
    loop_arc_predecessors = set(ξ.sample(range(n - 1), nb_loop_arcs))
    tree_nodes = set([0])
    bar = Bar("tree arcs", max=n-1)

    def dive(u):
        """Add loop arcs to tree where possible"""
        while u in loop_arc_predecessors:
            tree_nodes.add(u + 1)
            bar.next()
            yield (u, u + 1)
            u += 1

    # Keep track of nodes without parents in the tree or in the loop arcs. We ignore
    # loop arcs as they will be added by diving when the predecessor is added.
    parentless = set(range(1, n)) - set([u + 1 for u in loop_arc_predecessors])
    # Source node must have at least one child, choose from parentless nodes
    if 0 not in loop_arc_predecessors:
        v = ξ.choice(list(parentless))
        parentless.remove(v)
        bar.next()
        yield (0, v)
        yield from dive(v)
    else:
        yield from dive(0)
    # Remaining nodes must have exactly one parent, choose from nodes in tree.
    parentless = list(parentless)
    ξ.shuffle(parentless)
    for v in parentless:
        tree_nodes_list = list(tree_nodes)
        u = ξ.choice(tree_nodes_list)
        tree_nodes.add(v)
        bar.next()
        yield (u, v)
        yield from dive(v)
    bar.finish()


# ----------------------------------------------------------
def gen_loop_arcs(ξ, graph, distances, nb_neg_loop_arcs_remaining):
    n = graph.number_of_nodes()

    def determine_if_negative(u, v):
        return distances[u] > distances[v] and nb_neg_loop_arcs_remaining > 0

    order = list(range(n))
    ξ.shuffle(order)
    bar = Bar("loop arcs", max=n)
    for u in range(n):
        v = (u + 1) % n
        if (u, v) not in graph._arcs.keys():
            is_negative = determine_if_negative(u, v)
            if is_negative:
                nb_neg_loop_arcs_remaining -= 1
            bar.next()
            yield (u, v, is_negative)
    bar.finish()


# -----------------------------------------------------------
def determine_predecessor_vacancies(graph, order):
    """    
    A vacancy represents the lack of an inward arc to a node
    from a given predecessor.

    <- right-to-left arrow from high distances to low distances
    -> left-to-right arrow from low distances to high distances
     """
    n = graph.number_of_nodes()
    pos = {v: pos for pos, v in enumerate(order)}
    vacancies = {
        "<-": {i: n - 1 - pos[i] for i in range(n)},
        "->": {i: pos[i] for i in range(n)},
    }
    for v in range(n):
        for u, _ in graph.predecessors(v):
            if pos[v] < pos[u]:
                vacancies["<-"][v] -= 1
            else:
                vacancies["->"][v] -= 1
    return vacancies


def allocate_predecessors_to_nodes(ξ, graph, vacancies, m_pos, m_neg):
    """
    Negative arcs (really <=) must be allocated to <- vacancies 
    Positive arcs (really >=) can be allocated to both <- and -> vacancies
    """
    allocation = {"<=": distribute(ξ, vacancies["<-"], m_neg)}
    remaining_combined_vacancies = {
        i: vacancies["->"][i] + vacancies["<-"][i] - allocation["<="][i]
        for i in graph.nodes()
    }
    allocation[">="] = distribute(ξ, remaining_combined_vacancies, m_pos)
    return allocation


def gen_remaining_arcs(
    ξ, graph, distances, n, m, m_neg_total,
):
    m_remaining = max(0, m - graph.number_of_arcs())
    #assert m_remaining >= 0
    order = determine_order(distances)
    arc_vacancies = determine_predecessor_vacancies(graph, order)
    negative_arc_vacancies = sum(q for q in arc_vacancies["<-"].values())
    m_neg = max(min(nb_neg_remaining(graph, m_neg_total), m_remaining, negative_arc_vacancies),0)
    m_pos = m_remaining - m_neg
    total_capacity = negative_arc_vacancies + sum(
        q for q in arc_vacancies["->"].values()
    )
    assert negative_arc_vacancies >= m_neg
    assert total_capacity >= m_pos + m_neg, ""
    allocation = allocate_predecessors_to_nodes(ξ, graph, arc_vacancies, m_pos, m_neg)
    total = sum(q for x in allocation.values() for q in x.values())
    assert total == m_remaining
    # Generate predecessors
    def generate_arcs(sample_range, q, threshold=0, shuffle=False):
        """Can be used for both for both <- and -> arcs"""
        samples = ξ.sample(sample_range, min(q + 2, len(sample_range)))
        if shuffle:
            ξ.shuffle(samples)
        count = 0
        while count < q:
            s = samples.pop()
            u = order[s]
            if (u, v) not in graph._arcs:
                is_negative = count < threshold
                count += 1
                bar.next()
                yield u, v, is_negative

    bar = Bar("remaining arcs", max=max(m_remaining, 1))
    for pos, v in enumerate(order):
        total_allocation = allocation[">="][v] + allocation["<="][v]
        low_int = max(0, allocation[">="][v] - arc_vacancies["->"][v])
        high_int = min(allocation[">="][v], arc_vacancies["<-"][v] - allocation["<="][v])
        nb_pos_to_the_left = ξ.randint(
            a=low_int,
            b=high_int,
        )
        assert nb_pos_to_the_left >= 0, f"{nb_pos_to_the_left=}"
        nb_to_the_left = allocation["<="][v] + nb_pos_to_the_left
        nb_to_the_right = allocation[">="][v] - nb_pos_to_the_left
        assert nb_to_the_left + nb_to_the_right == total_allocation
        assert nb_to_the_left >= 0
        assert nb_to_the_right>= 0
        # Generate to the left <-
        if nb_to_the_left > 0:
            yield from generate_arcs(
                sample_range=range(pos + 1, n),
                q=nb_to_the_left,
                threshold=allocation["<="][v],
                shuffle=True,
            )
        # Generate to the right ->
        if nb_to_the_right > 0:
            yield from generate_arcs(sample_range=range(pos), q=nb_to_the_right)

    bar.finish()
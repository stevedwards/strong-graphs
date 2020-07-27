import math
from collections import defaultdict, OrderedDict
from strong_graphs.utils import distribute, determine_order
from typing import Dict, Hashable, List


__all__ = ["gen_remaining_arcs"]



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
    ξ, graph, distances, n,  m, r,
):  
    m_remaining = m - graph.number_of_arcs()
    order = determine_order(distances)
    arc_vacancies = determine_predecessor_vacancies(graph, order)
    negative_arc_vacancies = sum(q for q in arc_vacancies["<-"].values())
    m_neg = min(math.floor(r*m_remaining), negative_arc_vacancies) 
    m_pos = m_remaining - m_neg
    total_capacity = negative_arc_vacancies + sum(q for q in arc_vacancies["->"].values())
    assert negative_arc_vacancies >= m_neg, ""
    assert total_capacity >= m_pos + m_neg, ""
    allocation = allocate_predecessors_to_nodes(ξ, graph, arc_vacancies, m_pos, m_neg)
    # Generate predecessors
    def generate_arcs(sample_range, q, threshold=0, shuffle=False):
        """Can be used for both for both <- and -> arcs"""
        samples = ξ.sample(sample_range, min(q+2, len(sample_range)))
        if shuffle:
            ξ.shuffle(samples)
        count = 0
        while count < q:
            s = samples.pop()
            u = order[s]
            if (u, v) not in graph._arcs:
                is_negative = count < threshold
                count += 1
                yield u, v, is_negative

    for pos, v in enumerate(order):
        nb_pos_to_the_left = ξ.randint(
            a=max(0, allocation[">="][v] - arc_vacancies["->"][v]),
            b=min(m_pos, arc_vacancies["<-"][v] - allocation["<="][v]),
        )
        assert nb_pos_to_the_left >= 0, f"{nb_pos_to_the_left=}"
        nb_to_the_left = allocation["<="][v] + nb_pos_to_the_left
        nb_to_the_right = allocation[">="][v] - nb_pos_to_the_left
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
            yield from generate_arcs(
                sample_range=range(pos),
                q=nb_to_the_right              
            )
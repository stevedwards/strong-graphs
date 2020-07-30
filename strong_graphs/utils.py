import math
import statistics
from collections import defaultdict
from typing import Hashable, Dict, List, Tuple
import random


def nb_arcs_from_density(n: int, d: int) -> int:
    """
    Determines how many arcs in a directed graph of n and density d.
    Using a function I derived that had the follow characteristics
    m(d=0) = n, m(d=0.5) = (n)n-1/2 + 1, m(d=1) = n(n-1)
    """
    assert n > 1
    assert 0 <= d <= 1
    return (2 * n - 4) * d ** 2 + d * (n - 2) ** 2 + n


def nb_arcs_for_highest_neg_density(n: int) -> int:
    return nb_arcs_in_complete_dag(n) + 1


def nb_arcs_in_complete_dag(n):
    return round(n * (n - 1) / 2)


def determine_order(distances: Dict[Tuple, int]) -> List[Hashable]:
    """Sort tuple based on second value"""
    return [x[0] for x in sorted(list(distances.items()), key=lambda x: x[1])]


def shortest_path(tree):
    """Optimal path found using breadth first search on tree, O(n + m)"""
    distances = defaultdict(int)
    queue = set([0])
    while queue:
        u = queue.pop()
        for v, w in tree.successors(u):
            distances[v] = distances[u] + w
            queue.add(v)
    return distances


def distribute(
    random_state, capacity: Dict[Hashable, int], quantity: int
) -> Dict[Hashable, int]:
    """A method to distribute a quantity amongst choices with given capacities"""
    assert (
        total_capacity := sum(capacity.values())
    ) >= quantity, f"{quantity=} exceeds {total_capacity=}"
    choices = set(key for key, value in capacity.items() if value >= 1)
    allocation = defaultdict(int)
    for _ in range(quantity):
        select_node = random_state.choice(list(choices))
        allocation[select_node] += 1
        if allocation[select_node] == capacity[select_node]:
            choices.remove(select_node)
    return allocation

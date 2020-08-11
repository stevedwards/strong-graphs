import math
import statistics
from collections import defaultdict
from typing import Hashable, Dict, List, Tuple
from ordered_set import OrderedSet
import tqdm

def nb_arcs_from_density(n: int, d: int) -> int:
    """
    Determines how many arcs in a directed graph of n and density d.
    Using a function I derived that had the follow characteristics
    m(d=0) = n, m(d=0.5) = (n)n-1/2 + 1, m(d=1) = n(n-1)
    """
    assert n > 1
    assert 0 <= d <= 1
    return round((2 * n - 4) * d ** 2 + d * (n - 2) ** 2 + n)


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
    ξ, capacity: Dict[Hashable, int], quantity: int
) -> Dict[Hashable, int]:
    """A method to distribute a quantity amongst choices with given capacities"""
    total_capacity = sum(capacity.values())
    assert total_capacity >= quantity, f"{quantity=} exceeds {total_capacity=}"
    choices = [key for key, value in capacity.items() if value >= 1]
    ξ.shuffle(choices)
    choices = OrderedSet(choices)
    allocation = defaultdict(int)
    with tqdm.tqdm(total=quantity, desc="Distribute") as bar:
        for _ in range(quantity):
            bar.update()
            select_pos = ξ.randint(0, len(choices)-1)
            select_node = choices[select_pos]
            allocation[select_node] += 1
            if allocation[select_node] == capacity[select_node]:
                choices.remove(select_node)
    return allocation


def bellman_ford(graph, source):
    distances = defaultdict(lambda: float("inf"))
    distances[source] = 0
    queue = set([source])
    while queue:
        new_queue = set()
        for u in queue:
            for v, w in graph.successors(u):
                if distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    new_queue.add(v)
        queue = new_queue
    return distances

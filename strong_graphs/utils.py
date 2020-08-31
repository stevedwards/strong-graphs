import math
import statistics
from collections import defaultdict
from typing import Hashable, Dict, List, Tuple
from ordered_set import OrderedSet
import tqdm
from bisect import bisect_left, bisect_right


def take_closest(myList, myNumber):
    """
    Assumes myList is sorted. Returns closest value to myNumber.

    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
       return after
    else:
       return before

def find_ge(a, x):
    "Find leftmost item greater than or equal to x"
    i = bisect_left(a, x)
    if i != len(a):
        return a[i]
    raise ValueError


def find_le(a, x):
    "Find rightmost value less than or equal to x"
    i = bisect_right(a, x)
    if i:
        return a[i - 1]
    raise ValueError


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


def bellman_ford(graph, source, unit_weight=True):
    distances = defaultdict(lambda: float("inf"))
    distances[source] = 0
    queue = set([source])
    while queue:
        new_queue = set()
        for u in queue:
            for v, w in graph.successors(u):
                if unit_weight:
                    w = 1
                if distances[u] + w < distances[v]:
                    distances[v] = distances[u] + w
                    new_queue.add(v)
        queue = new_queue
    return distances

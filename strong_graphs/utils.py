import math
from collections import defaultdict
from typing import Hashable, Dict


def nb_arcs_from_density(n: int, d: int) -> int:
    """Determines how many arcs in a directed graph of n and density d"""
    return n + math.floor(d * n * (n - 2))

def distribute(
    random_state, capacity: Dict[Hashable, int], quantity: int
) -> Dict[Hashable, int]:
    """A method to distribute a quantity amongst choices with given capacities"""
    choices = set(key for key, value in capacity.items() if value >= 1)
    allocation = defaultdict(int)
    for _ in range(quantity):
        select_node = random_state.choice(list(choices))
        allocation[select_node] += 1
        if allocation[select_node] == capacity[select_node]:
            choices.remove(select_node)
    return allocation

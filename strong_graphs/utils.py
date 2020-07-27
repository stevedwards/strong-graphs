import math
import statistics
from collections import defaultdict
from typing import Hashable, Dict, List, Tuple
import random

def nb_arcs_from_density(n: int, d: int) -> int:
    """Determines how many arcs in a directed graph of n and density d"""
    return n + math.floor(d * n * (n - 2))


def determine_order(distances: Dict[Tuple, int]) -> List[Hashable]:
    """Sort tuple based on second value"""
    return [x[0] for x in sorted(list(distances.items()), key=lambda x: x[1])]


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



def determine_alpha_beta(μ, control=100.0):
    """The mean of the beta distribution is

    μ = α / (α + β) => μ (α + β) = α
                        β = α(1 - μ) / μ
                        or μ α - α = - β μ
                          α(1 - μ) = βμ
                                α = β.μ/(1-μ)
    """
    assert 0 <= μ <= 1, "Mean must be valid"
    if μ > 0.5:
        α = control
        β = α * (1 - μ) / μ
    else:
        β = control
        α = β * μ / (1 - μ)
    return α, β


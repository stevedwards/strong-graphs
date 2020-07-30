from strong_graphs.utils import nb_arcs_from_density, nb_arcs_in_complete_dag
import random
from numpy import nextafter

__all__ = [
    "nb_neg_arcs",
    "nb_neg_tree_arcs",
    "nb_neg_loop_arcs",
]


def determine_alpha_beta(μ, control=100.0):
    """
    Beta distributions are used to choose the number of negative arcs at 
    different stages, i.e., how many negative arcs are 
    - in the optimal tree 
    - in the loop
    - in the remaining arcs
    This ensure the number of negative arcs adds up to the total while 
    ensuring the generator is still complete.

    This function calculates the parameters of the beta distribution for
    a desired mean.
    μ = α / (α + β) => β = α(1 - μ) / μ or α = β.μ/(1-μ)
    """
    assert 0 <= μ <= 1, f"Mean must be valid {μ=}"
    if μ > 0.5:
        α = control
        β = α * (1 - μ) / μ
    else:
        β = control
        α = β * μ / (1 - μ)
    return α, β


def sample_number(ξ, min_value, max_value, expected) -> int:
    """Infers a beta distribution with given parameters """
    assert max_value >= expected >= min_value
    if max_value - min_value == 0:
        return max_value
    else:
        μ = (expected - min_value) / (max_value - min_value)
        μ = nextafter(μ, 0.5)
        α, β = determine_alpha_beta(float(μ))
        x = ξ.betavariate(α, β)
        return round(min_value + x * (max_value - min_value))


def nb_neg_arcs(n, m, r):
    """ The total number of negative arcs is decided by the ratio
    but capped at the number corresponding to a complete DAG"""
    m_dag = nb_arcs_in_complete_dag(n)
    return min(round(r * (m-1)), m_dag)


def nb_neg_tree_arcs(ξ, n, m, m_neg):
    assert m_neg < m
    m_neg_tree_max = min(n - 1, m_neg)
    expected = (m_neg / m) * (n - 1)
    x = sample_number(ξ, min_value=0, max_value=m_neg_tree_max, expected=expected)
    return x


def nb_neg_loop_arcs(ξ, n, m, m_neg, m_neg_tree, m_neg_tree_loop):
    """Assumes the graph already contains a tree"""
    remaining_arcs = m - (n - 1)  # Where n - 1 is the arcs in the tree
    remaining_neg = m_neg - m_neg_tree
    ratio = remaining_neg / remaining_arcs
    min_value = max(m_neg_tree_loop, m_neg - nb_arcs_in_complete_dag(n-1))
    expected = max(ratio * (n - 1), min_value)
    max_value = min(n - 1, m_neg)
    x = sample_number(ξ, min_value, max_value, expected)
    return x

def nb_neg_remaining(network, m_neg):
    """Note here the <= is deliberate as some negative arcs might be forced to 0
    given pre-existing distributions. 
    """ 
    return m_neg - sum(1 for u,v,w in network.arcs() if w <= 0)


if __name__ == "__main__":
    # TODO turn this into a hypothesis for general n, d, r
    n = 10
    d = 1
    r = 1
    ξ = random.Random(0)
    m = nb_arcs_from_density(n, d)
    m_neg = nb_neg_arcs(n, m, r)
    assert 0 <= m_neg < m
    m_neg_tree = nb_neg_tree_arcs(ξ, n, m, m_neg)
    assert 0 <= m_neg_tree <= n - 1
    m_neg_tree_loop = ξ.randint(0, m_neg_tree)
    m_neg_loop = nb_neg_loop_arcs(
        ξ, n, m, m_neg, m_neg_tree, m_neg_tree_loop
    )
    assert 0 <= m_neg_loop <= n - 1
    assert m_neg_loop <= m_neg - m_neg_tree

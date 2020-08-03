import pytest
from hypothesis import given
import hypothesis.strategies as st
from numpy import nextafter
import math
import random
from strong_graphs.negative import (
    determine_alpha_beta,
    sample_number,
    nb_neg_arcs,
    nb_neg_tree_arcs,
    nb_neg_loop_arcs,
)

max_int = 10000

@given(st.floats(min_value=0, max_value=1))
def test_determine_alpha_beta(μ):
    α, β = determine_alpha_beta(μ)
    x = α / (α + β)
    assert math.isclose(μ, x, abs_tol=1e-09)


@given(
    st.tuples(st.integers(max_value=max_int), st.integers(max_value=max_int))
)
def test_sample_number(two_ints):
    min_value, max_value = min(two_ints), max(two_ints)
    ξ = random.Random()
    μ = ξ.randint(min_value, max_value)
    x = sample_number(ξ, min_value, max_value, μ)
    assert min_value <= x <= max_value
    assert isinstance(x, int)


@given(
    st.integers(min_value=2, max_value=max_int), st.floats(min_value=0, max_value=1)
)
def test_nb_neg_arcs(n, r):
    ξ = random.Random(1)
    m = ξ.randint(n, n * (n - 1))
    # Number of negative arcs
    m_neg = nb_neg_arcs(n, m, r)
    assert 0 <= m_neg < m
    assert m_neg <= n * (n - 1) / 2
    # Number of tree arcs
    m_neg_tree = nb_neg_tree_arcs(ξ, n, m, m_neg)
    assert 0 <= m_neg_tree < n
    assert m_neg_tree <= m_neg
    # Number of loop arcs
    m_neg_tree_loop = ξ.randint(0, m_neg_tree)
    m_neg_loop = nb_neg_loop_arcs(ξ, n, m, m_neg, m_neg_tree, m_neg_tree_loop)
    assert m_neg_tree_loop <= m_neg_loop < n

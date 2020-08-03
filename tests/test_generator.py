import random
from functools import partial
import pytest
from strong_graphs.generator import build_instance
from strong_graphs.negative import nb_neg_arcs
from strong_graphs.utils import nb_arcs_from_density
from hypothesis import given
import hypothesis.strategies as st

@pytest.mark.parametrize(
    "n, d, r, D_", [(20, 0.25, 0.5, (-100, 100)), (20, 0.25, 0.5, (-100, 100))]
)
def test_seed_consistency(n, d, r, D_):
    """ Seed consistency checker: verify that using the same seed gives the
    same result, and different seeds give different results. Could make this
    a fuzzy test by generating random values for other parameters. """
    seed1, seed2 = 25, 23857235
    instances = []
    m = nb_arcs_from_density(n, d)
    for seed in (seed1, seed1, seed2):
        # Replicates what's in the CLI at the moment.
        ξ = random.Random(seed)
        D = partial(random.Random.randint, a=D_[0], b=D_[1])
        instances.append(build_instance(ξ, n, m, r, D))
    (
        (net1, tree1, dist1, map1),
        (net2, tree2, dist2, map2),
        (net3, tree3, dist3, _),
    ) = instances
    # Same seed matches.
    assert net1 == net2 and tree1 == tree2 and dist1 == dist2 and map1 == map2
    # Different seeds mismatch.
    assert net1 != net3 and tree1 != tree3 and dist1 != dist3 


@given(
    st.integers(min_value=2, max_value=100), 
    st.floats(min_value=0, max_value=1),
    st.floats(min_value=0, max_value=1),
    st.integers(min_value=1, max_value=100000),
    st.integers(min_value=1, max_value=100000),
)
def test_generator(n, d, r, D_min, D_max):
    m = nb_arcs_from_density(n, d)
    D = partial(random.Random.randint, a=-D_min, b=D_max)
    ξ = random.Random(1)
    net, tree1, dist1, map1 = build_instance(ξ, n, m, r, D)

    assert  m <= net.number_of_arcs() <= m+n-1
    nb_non_pos = sum(1 for u, v, w in net.arcs() if w <= 0)
    m_neg = nb_neg_arcs(n, d, r)
    assert nb_non_pos >= m_neg
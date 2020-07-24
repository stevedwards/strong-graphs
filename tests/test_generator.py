import random
from functools import partial
import pytest
from strong_graphs.generator import build_instance, distribute


@pytest.mark.parametrize(
    "n, m, x1, x2, ensure_non_negative",
    [(20, 360, (-100, 100), (0, 100), True), (10, 16, (-100, 100), (0, 100), False)],
)
def test_seed_consistency(n, m, x1, x2, ensure_non_negative):
    """ Seed consistency checker: verify that using the same seed gives the
    same result, and different seeds give different results. Could make this
    a fuzzy test by generating random values for other parameters. """
    seed1, seed2 = 25, 23857235
    instances = []
    for seed in (seed1, seed1, seed2):
        # Replicates what's in the CLI at the moment.
        random_state = random.Random(seed)
        instances.append(
            build_instance(
                random_state,
                n,
                m,
                tree_weight_distribution=partial(random.Random.randint, a=x1[0], b=x1[1]),
                non_tree_weight_distribution=partial(random.Random.randint, a=x1[0], b=x2[1]),
                arc_distribution=distribute_remaining_arcs_randomly,
                ensure_non_negative=ensure_non_negative,
            )
        )
    (net1, tree1, dist1), (net2, tree2, dist2), (net3, tree3, dist3) = instances
    # Same seed matches.
    assert net1 == net2 and tree1 == tree2 and dist1 == dist2
    # Different seeds mismatch.
    assert net1 != net3 and tree1 != tree3 and dist1 != dist3

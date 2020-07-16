import random

import pytest

from strong_graphs.generator import build_instance, distribute_remaining_arcs_randomly


@pytest.mark.parametrize("nodes, edges, ensure_non_negative", [(20, 360, True), (10, 16, False)])
def test_build_instance(nodes, edges, ensure_non_negative):
    random.seed(0)
    network, tree, distances = build_instance(
        nodes,
        edges,
        tree_weight_distribution=lambda: random.randint(-100, 100),
        non_tree_weight_distribution=lambda: random.randint(0, 100),
        arc_distribution=distribute_remaining_arcs_randomly,
        ensure_non_negative=ensure_non_negative,
    )

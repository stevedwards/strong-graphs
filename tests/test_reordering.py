import pytest
import random
from strong_graphs.loop_arcs import (
    reorder_nodes,
    count_left_arcs,
    correct_node_position,
)

def test_node_map():
    n = 10
    x = 9
    order = list(range(n))
    random.shuffle(order)
    new_order = reorder_nodes(order, x)
    assert len(set(new_order)) == n
    assert count_left_arcs(new_order) >= x

def test_correct():
    order = [1, 0, 2, 3]
    order = correct_node_position(order, 1)
    assert order == [1, 3, 2, 0]

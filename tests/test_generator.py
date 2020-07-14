import pytest
from generator.generate import create_optimal_tree

def test_tree_generator():
    n = 4
    m = 5
    tree = create_optimal_tree(n, m)
    assert len(tree._children[0]) > 0, "source must have at least one successor"
    for i in range(1, n):
        assert tree._parent.get(i, None) is not None, f"{i=} has no parent"
    return tree


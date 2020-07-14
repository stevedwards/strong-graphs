import random
import math
from strong_graphs.generate import distribute_remaining_arcs_randomly, build_instance
from strong_graphs.draw import draw_graph

if __name__ == "__main__":
    #random.seed(1)
    n = 24
    d = 0.2
    m = n + math.floor(d * n * (n - 2))
    print(f"{n=}, {d=}, {m=}")
    D1 = lambda: random.randint(-100, 0)
    D2 = lambda: random.randint(0, 10)  # Must be non-negative
    D3 = distribute_remaining_arcs_randomly
    instance, tree, distances = build_instance(
        n,
        m,
        tree_weight_distribution=D1,
        non_tree_weight_distribution=D2,
        arc_distribution=D3,
        ensure_non_negative=False,
    )

    draw_graph(instance, tree, distances)
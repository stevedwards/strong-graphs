import random
import math
from functools import partial
import click
from strong_graphs.generator import distribute_remaining_arcs_randomly, build_instance
from strong_graphs.draw import draw_graph
from strong_graphs.output import output


# Command line information
@click.command()
@click.argument("n", type=int)
@click.option("-d", type=float, default=1, help="Density, d∈[0,...,1] (1)")
@click.option('-s', type=float, default=0, help="Random seed (0)")
@click.option('-m', type=int, default=None, help="Number of arcs override (None)")
@click.option('-x1', type=(float, float), default=(-100, 100), help="Optimal tree distribution bounds (-100, 100)")
@click.option('-x2', type=(float, float), default=(0, 100), help="Remaining arc distribution bounds (0, 100)")
@click.option('-ensure_non_neg', type=bool, default=False, help="Ensure remaining arc weights are non-negative (False)")
 
def generate(n, d, s, m, x1, x2, ensure_non_neg):
    assert 0 <= d <= 1, f"Density {d} must be between 0 and 1"
    assert x2[0] >= 0, f"Remaining arc distribution must be non-negative, given {x2=}"
    if m is None:
        m = n + math.floor(d * n * (n - 2))
    else:
        print(f"Density value {d=} is being overriden by {m=}")
    # Print parameter information
    print(f"""
    Generating a strong graph (💪) with the following parameters
    - Number of nodes, {n=}
    - Number of arcs, {m=}
    - Tree distribution parameters, {x1=}
    - Other distribution parameters, {x2=}
    - Random seed, {s=}
    - Ensuring other arcs are non-neg, {ensure_non_neg=}
    """)
    random_state = random.Random(s)
    network, tree, distances = build_instance(
        random_state,
        n,
        m,
        tree_weight_distribution=partial(random.Random.randint, a=x1[0], b=x1[1]),
        non_tree_weight_distribution=partial(random.Random.randint, a=x1[0], b=x2[1]),
        arc_distribution=distribute_remaining_arcs_randomly,
        ensure_non_negative=ensure_non_neg,
    )
    draw_graph(network, tree, distances)
    sum_of_distances = sum(distances.values())
    output(network, sum_of_distances)


generate()  # pylint: disable=no-value-for-parameter

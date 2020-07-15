import random
import math
from strong_graphs.generate import distribute_remaining_arcs_randomly, build_instance
from strong_graphs.draw import draw_graph
import click


@click.command()
@click.argument("n", type=int)
@click.argument("d", type=float)

def generate(n, d):
    random.seed(3)
    # Infer from density
    m = n + math.floor(d * n * (n - 2))
    print(f"{n=}, {d=}, {m=}")
    D1 = lambda: random.randint(-100, -100)
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
# @click.option(
#     "--d", default=1, type=float, help="Density of graph - 0: cycle, 1:complete"
# )
# @click.option("--m", default=None, type=int, help="Option to select specific number of arcs, this overides the density value")
# @click.option(
#     "--D1",
#     default="randint",
#     type=click.Choice(["randint", "normal"]),
#     help="Distribution from which arcs weights for optimal path arcs are sampled",
# )

generate()
import random
import math
from functools import partial
import click
from strong_graphs.generator import build_instance, determine_n, change_source_nodes
from strong_graphs.output import output
from strong_graphs.utils import nb_arcs_from_density


# Command line information
# @click.command()
# @click.argument("m", type=int)
# @click.argument("s", type=int)
def generate_from_distribution(m, s):
    ξ = random.Random(s)
    d = ξ.random()

    n = determine_n(m, d)
    z = ξ.randint(1, n)
    r = ξ.random()
    #r = 0.001
    lb = ξ.randint(-10000, 0)
    ub = ξ.randint(0, 10000)
    print(n, m)
    D = partial(random.Random.randint, a=lb, b=ub)
    network, _, distances, _, source = build_instance(
        ξ,
        n,
        m,
        r,
        D
    )
    
    sum_of_distances = 0 #sum(distances.values())
    change_source_nodes(ξ, network, z)
    output(ξ, network, sum_of_distances, m, d, r, s, lb, ub, -1)

generate_from_distribution(1000, 0)  # pylint: disable=no-value-for-parameter
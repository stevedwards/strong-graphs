import random
import math
from functools import partial
import click
from strong_graphs.generator import build_instance, determine_n, change_source_nodes
from strong_graphs.output import output
from strong_graphs.utils import nb_arcs_from_density


# Command line information
@click.command()
@click.argument("m", type=int)
@click.argument("s", type=int)
@click.argument("is_int", type=bool)
def generate_from_distribution(m, s, is_int):
    ξ = random.Random(s)
    d = ξ.random()
    n = determine_n(m, d)
    z = ξ.randint(1, n)
    r = ξ.random()
    #r = 0.001
    C_proxy = ξ.randint(0, 10)
    lb = ξ.uniform(-10**C_proxy, 0)
    ub = ξ.uniform(0, 10**C_proxy)
    if is_int:
        lb = round(lb)
        ub = round(ub)
    print(n, m)
    D = partial(random.Random.randint if is_int else random.Random.uniform, a=lb, b=ub)
    network, _, distances, _, source = build_instance(
        ξ,
        n,
        m,
        r,
        D
    )
    if not is_int:
        network = network.normalise()
    
    sum_of_distances = 0 #sum(distances.values())
    change_source_nodes(ξ, network, z)
    output(ξ, network, sum_of_distances, m, d, r, s, z, lb, ub, -1)

generate_from_distribution()  # pylint: disable=no-value-for-parameter
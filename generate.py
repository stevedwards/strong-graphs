import random
import math
from functools import partial
import click
from strong_graphs.generator import build_instance, determine_n
from strong_graphs.output import output
from strong_graphs.utils import nb_arcs_from_density

# Command line information
@click.command()
@click.argument("n", type=int)
@click.option("-d", type=float, default=0.1, help="Density, d∈[0,...,1] (1)")
@click.option('-r', type=float, default=0.25, help="Proporition of negative remaining arcs, (0 ≤ r ≤ 1)")
@click.option('-m', type=int, default=None, help="Number of arcs override (None)")
@click.option('-lb', type=int, default=-100000, help="Lower bound to distribution")
@click.option('-ub', type=int, default=100000, help="Upper bound to distribution")
@click.option('-s', type=int, default=0, help="Random seed (0)")
@click.option('-is_integer', type=bool, default=True, help="Boolean to indicate if arc weights are integer or floats (True)")
def generate(n, d, r, m, lb, ub, s, is_integer, verbose=False):
    assert 0 <= d <= 1, f"Density {d} must be between 0 and 1"
    assert 0 <= r <= 1, f"Proportion of negative remaining arcs between 0 and 1, {r=}"
    assert lb <= 0, f"Lower bound of arc distribution must be non-positive, {lb=}"
    assert ub >= 0, f"Upper bound of arc distribution must be non-negative,  {ub=}"
    if m is None:
        m = nb_arcs_from_density(n, d)
    elif verbose:
        print(f"Density value {d=} is being overriden by {m=}")
    
    #m_neg = min(r * (m-1), (n)*(n-1)/2)
    # Print parameter information
    if verbose:
        print(f"""
        Generating a strong graph (💪) with the following parameters
        - Number of nodes, {n=}
        - Density, {d=}
        - Negative arc ratio, {r=}
        - Number of arcs, {m=}
        - Distribution, [{lb=}, {ub=}]
        - Random seed, {s=}
        - Integer arc weights, {is_integer=}
        """)
    ξ = random.Random(s)
    D = partial(random.Random.randint if is_integer else random.Random.uniform, a=lb, b=ub)
    network, _, distances, _, source = build_instance(
        ξ,
        n,
        m,
        r,
        D
    )
    sum_of_distances = sum(distances.values())
    output(ξ, network, sum_of_distances, d, r, s, lb, ub, source)



# Command line information
@click.command()
@click.argument("m", type=int)
@click.argument("s", type=int)
def generate_from_distribution(m, s):
    ξ = random.Random(s)
    d = ξ.random()

    n = determine_n(m, d)
    r = ξ.random()
    #r = 0.001
    lb = ξ.randint(-10000, 0)
    ub = ξ.randint(0, 10000)
    #m = nb_arcs_from_density(n, d)
    #m = round(1.5*n)
    print(n, m)
    D = partial(random.Random.randint, a=lb, b=ub)
    network, _, distances, _, source = build_instance(
        ξ,
        n,
        m,
        r,
        D
    )
    sum_of_distances = sum(distances.values())
    output(ξ, network, sum_of_distances, m, d, r, s, lb, ub, source)

generate_from_distribution()  # pylint: disable=no-value-for-parameter
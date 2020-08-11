import sys
import tqdm
import statistics


def output(ξ, graph, sum_of_distances, d, r, s, lb, ub, source, shuffle=True, output_dir="output/", to_file=True):
    """
    Converts a graph in `extended DIMACS format' which is what is expected
    by the algorithms in SPLib
    
    Note that the node ordering is indexed from 1 not 0 so our nodes must be increased.
    """
    n = graph.number_of_nodes()
    m = graph.number_of_arcs()
    arc_weights = [w for _, _, w in graph.arcs()]
    m_neg = sum(1 for w in arc_weights if w < 0)
    m_zero = sum(1 for w in arc_weights if w == 0)
    filename = f"strong-graph-{n}-{s}"  # Other input data required
    if shuffle:
        nodes = list(range(n))
        ξ.shuffle(nodes)
        mapping = {u: i for i, u in enumerate(nodes)}
    else:
        mapping = {i: i for i in range(m)}

    with open(output_dir + filename, "w") if to_file else sys.stdout as f:  #
        f.write(
            f"""c Strong graph for shortest paths problem
c extended DIMACS format
c filename: {filename}
c 
c Generator Parameters
c {n=}
c {d=}
c {r=}
c {s=}
c {lb=}
c {ub=}
c
c Features
c Sum of distances {sum_of_distances}
c Number of arcs {m}
c Density {m / n**2}
c Proportion of negative arcs {m_neg}
c Proportion of zero arcs {m_zero}
c Number of positive arcs {m - m_neg - m_zero}
c Max arc weight {max(arc_weights)}
c Min arc weight {min(arc_weights)}
c Mean arc weight {statistics.mean(arc_weights)}
"""
        )
        f.write(f"t strong-graph-{n}-{s}\nc\n")
        f.write(f"p sp {n:10} {m:10}\nc\n")
        f.write(f"n {mapping[source]+1:10}\nc\n")
        with tqdm.tqdm(total=m, desc="Output") as bar:
            arcs = list(graph.arcs())
            ξ.shuffle(arcs)
            for u, v, w in arcs:
                bar.update()
                f.write(f"a {mapping[u]+1:10} {mapping[v]+1:10} {w:10}\n")

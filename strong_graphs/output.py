import sys
import tqdm
import statistics
from strong_graphs.utils import bellman_ford

def output(ξ, graph, sum_of_distances, target_n_arcs, d, r, s, z, lb, ub, source, shuffle=True, output_dir="output/", to_file=True):
    """
    Converts a graph in `extended DIMACS format' which is what is expected
    by the algorithms in SPLib
    
    Note that the node ordering is indexed from 1 not 0 so our nodes must be increased.
    """
    n_actual = graph.number_of_nodes()
    n_component = n_actual - 1
    m_actual = graph.number_of_arcs()
    m_component = target_n_arcs
    source_nodes = len(graph._successors[source])
    arc_weights = [w for _, _, w in graph.arcs()]
    m_neg = sum(1 for w in arc_weights if w < 0)
    min_abs = min(abs(w) for w in arc_weights if w != 0)
    max_abs = max(abs(w) for w in arc_weights)
    mean_abs = statistics.mean(abs(w) for w in arc_weights)
    var_abs = statistics.variance(abs(w) for w in arc_weights)
    m_zero = sum(1 for w in arc_weights if w == 0) - source_nodes
    filename = f"strong-graph-{m_component}-{s}"  # Other input data required
    if shuffle:
        nodes = list(graph.nodes())
        ξ.shuffle(nodes)
        mapping = {u: i for i, u in enumerate(nodes)}
    else:
        mapping = {i: i for i in range(m)}

    # Feature
    unit_distances = bellman_ford(graph, source, unit_weight=True)
    with open(output_dir + filename, "w") if to_file else sys.stdout as f:  #
        f.write(
            f"""c Strong graph for shortest paths problem
c extended DIMACS format
c filename: {filename}
c 
c Generator Parameters
c n={n_component}
c m={m_component}
c {d=}
c {r=}
c {s=}
c {lb=}
c {ub=}
c {z=}
c
c Features
c Number of nodes including dummy {n_actual}
c Number of arcs including dummy {m_actual}
c Sum of distances {sum_of_distances}
c Number of arcs {m_component}
c Density {m_component / n_component**2}
c Proportion of negative arcs {m_neg}
c Proportion of zero arcs {m_zero}
c Number of positive arcs {m_component - m_neg - m_zero}
c Max depth {max(unit_distances.values())}
c Weight max {max(arc_weights)}
c Weight min {min(arc_weights)}
c Weight mean {statistics.mean(arc_weights)}
c Weight variance {statistics.mean(arc_weights)}
c Abs weight max {max_abs}
c Abs weight min {min_abs}
c Abs weight mean {mean_abs}
c Abs weight variance {var_abs}
c Source nodes {source_nodes}
c Source node ratio {source_nodes/float(n_component)}
"""
        )
        f.write(f"t strong-graph-{m_component}-{s}\nc\n")
        f.write(f"p sp {n_actual:10} {m_actual:10}\nc\n")
        f.write(f"n {mapping[source]+1:10}\nc\n")
        with tqdm.tqdm(total=m_actual, desc="Output") as bar:
            arcs = list(graph.arcs())
            ξ.shuffle(arcs)
            for u, v, w in arcs:
                bar.update()
                f.write(f"a {mapping[u]+1:10} {mapping[v]+1:10} {w:10}\n")

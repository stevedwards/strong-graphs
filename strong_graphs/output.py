
def output(graph, sum_of_distances, output_dir="output/"):
    """
    Converts a graph in `extended DIMACS format' which is what is expected
    by the algorithms in SPLib
    
    Note that the node ordering is indexed from 1 not 0 so our nodes must be increased.
    """
    n = graph.number_of_nodes()
    m = graph.number_of_arcs()
    source = 0
    filename = f"strong-graph-{n}-{m}-{sum_of_distances}"    # Other input data required
    with open(output_dir+filename, 'w') as f:
        f.write("c Strong graph for shortest paths problem\n")
        f.write("c extended DIMACS format\nc\n")
        f.write(f"t {filename}\nc\n")
        # Skipping some bits
        f.write(f"p sp {n:10} {m:10}\nc\n")
        f.write(f"n {source+1:10}\nc\n")
        for u, v, w in graph.arcs():
            f.write(f"a {u+1:10} {v+1:10} {w:10}\n")
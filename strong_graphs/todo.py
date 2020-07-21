
def gen_loop_arcs(
    random_state,
    graph,
    distances,
    n,
    m,
    r,
):
    nb_unique_distances = len(set(distances.values()))
    remaining_arcs = m - graph.number_of_arcs()
    nb_negative_tree_arcs = sum(1 for u,v,w in graph.arcs() if w < 0)
    nb_negative_remaining_arcs = min(math.floor(r * remaining_arcs), n*(n-1)/2 - nb_negative_tree_arcs)
    nb_negative_loop_arcs_min = min(0, nb_negative_remaining_arcs - ((n-1)*(n*2)-nb_negative_tree_arcs))
    # The minimum number of loop arcs
    ordering = sorted(distances.items(), key=lambda x: x[1])
    nb_negative_loop_arcs = random_state.randint(0, min(nb_negative_arcs, n-1, ))
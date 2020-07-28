import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.animation import FuncAnimation, PillowWriter
from strong_graphs.generator import build_instance
from strong_graphs.draw import curved_arcs
from draw import circle_layout
import random
from functools import partial
import itertools
from matplotlib.colors import ListedColormap
from palettable.cartocolors.diverging import Tropic_2
from progress.bar import Bar
import math

def animate(network, tree_arcs, distances, mapping):
    n = network.number_of_nodes()
    G = nx.DiGraph()
    curviture = 0.1
    non_tree_arcs = []
    for i in range(n):
        G.add_node(i)
    for u, v, w in network.arcs():
        if (u, v) not in tree_arcs:
            non_tree_arcs.append((u, v))
        G.add_edge(u, v, weight=w)
    tree_arcs = list(tree_arcs)
    plt.axis("off")
    pos = circle_layout(n)
    fig, ax = plt.subplots(1, 1, figsize=(5, 5))

    def draw_nodes(graph):
        for i in range(n):
            relevant_pos = {i: pos[i]}
            yield (
                nx.draw_networkx_nodes(
                    graph, relevant_pos, [i], node_color="xkcd:dark sky blue", ax=ax
                ),
            ) if graph else 0

    def draw_tree(graph):
        for u, v in tree_arcs:
            yield (
                nx.draw_networkx_edges(
                    graph,
                    pos,
                    edgelist=[(u, v)],
                    ax=ax,
                    edge_color="xkcd:red",
                    connectionstyle=curved_arcs(curviture),
                )[0],
            ) if graph else 0

    colours = ListedColormap(Tropic_2.mpl_colors)
    def draw_remaining_arcs(graph):
        for u, v in non_tree_arcs:
            w = network._arcs[(u, v)]
            colour = colours(0) if w > 0 else colours(1)
            yield (nx.draw_networkx_edges(
                    graph,
                    pos,
                    edgelist=[(u, v)],
                    ax=ax,
                    style="dashed",
                    width=0.5,
                    edge_color=colour,
                    connectionstyle=curved_arcs(curviture),
                )[0],) if graph else 0

    def generate_frame(graph=None):
        
        yield from draw_nodes(graph)
        yield from draw_tree(graph)
        yield from draw_remaining_arcs(graph)

    frames = generate_frame(G)
    num_frames = sum(1 for _ in generate_frame(None))
    
    bar = Bar(max=num_frames)
    def update(i):
        bar.next()
        return next(frames)

    # output animation; its important I save it
    ani = FuncAnimation(
        fig, update, interval=1, repeat_delay=1000, frames=range(num_frames - 2), blit=False
    )
    bar.finish()
    ani.save("strong.gif", writer='imagemagick', savefig_kwargs={"facecolor": "white"})


if __name__ == "__main__":
    random_state = random.Random(0)
    n = 20  # Number of nodes
    d = 1  # Density
    r = 1  # Ratio of negative arcs
    m = n + math.floor(d * n * (n - 2))
    #m = int(n * (n - 1) / 2) + 1
    print("Building graph")
    network, tree_arcs, distances, mapping = build_instance(
        random_state,
        n=n,
        m=m,
        r=r,
        D_tree=partial(random.Random.randint, a=-1000, b=-1),  # -100000, b=-1),
        D_remaining=partial(random.Random.randint, a=0, b=1000),
    )
    print("Creating gif")
    animate(network, tree_arcs, distances, mapping)

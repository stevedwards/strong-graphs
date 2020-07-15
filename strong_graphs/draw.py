import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import math
import networkx as nx
from strong_graphs.data_structures.networks import to_networkx
from matplotlib.colors import ListedColormap
from palettable.cartocolors.diverging import Tropic_2


def curved_arcs(radius):
    """Returns string required for networkx 'connectionstyle' keyword to generate 
    curved arcs"""
    return f"arc3, rad={radius}"


def circle_layout(graph):
    """Custom node layout to have nodes positioned in an anti-clockwise circle starting from
    the middle left"""
    n = graph.number_of_nodes()
    frac = 2 * math.pi / n
    return {i: (-math.cos(i * frac), -math.sin(i * frac)) for i in graph.nodes()}


def draw_heatmap_graph(nx_graph, layout, ax, fig, curviture=0.1, cmap=mpl.cm.plasma):
    """Draws the graphs where arc weights are indicated using a heatmap"""
    weights = [w for _, _, w in nx_graph.edges.data("weight", default=None)]
    max_edge_abs = max(max(weights), -min(weights))
    norm = mpl.colors.Normalize(vmin=-max_edge_abs, vmax=max_edge_abs)
    nx.draw_networkx(
        nx_graph,
        node_color="xkcd:dark sky blue",
        pos=layout,
        with_labels=False,
        ax=ax,
        edge_color=[cmap(norm(x)) for x in weights],
        connectionstyle=curved_arcs(curviture),
        edge_cmap=cmap,
    )
    fig.colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=ax,
        orientation="horizontal",
        shrink=0.25,
        label="Arc Weight",
    )


def draw_solution_tree_graph(
    nx_graph, nx_tree, layout, ax, fig, curviture=0.1, cmap=mpl.cm.Oranges
):
    """Draws a shortest path tree over the top of the graph. The arcs in the tree
    are highlighted in red."""
    nx.draw_networkx(
        nx_graph,
        node_color="xkcd:dark sky blue",
        pos=layout,
        ax=ax,
        edge_color="xkcd:light grey",
        connectionstyle=curved_arcs(curviture),
    )
    nx.draw_networkx_edges(
        nx_tree,
        pos=layout,
        ax=ax,
        connectionstyle=curved_arcs(curviture),
        edge_color="xkcd:red",
    )
    fig.colorbar(
        mpl.cm.ScalarMappable(cmap=cmap),
        ax=ax,
        orientation="horizontal",
        shrink=0.25,
        label="Arcs in Optimal Shortest Path",
    )


def draw_arc_sign_graph(
    nx_graph, layout, ax, fig, curviture=0.1, cmap=ListedColormap(Tropic_2.mpl_colors)
):
    """Draws the graphs where the sign, i.e. negative (<) or non-negative (≥), is indicated by
    different colours."""
    neg_colour, non_neg_colour = cmap(0), cmap(1)
    edge_colours = [
        neg_colour if w >= 0 else non_neg_colour
        for _, _, w in nx_graph.edges.data("weight", default=None)
    ]
    nx.draw_networkx(
        nx_graph,
        pos=layout,
        with_labels=False,
        node_color="xkcd:dark sky blue",
        edge_color=edge_colours,
        style="dashdot",
        connectionstyle=curved_arcs(curviture),
    )
    fig.colorbar(
        mpl.cm.ScalarMappable(cmap=cmap),
        ax=ax,
        orientation="horizontal",
        shrink=0.25,
        label="Non-Negative vs Negative Arc weights",
    )
    plt.show()


def draw_graph(graph, tree, distances):
    """Draws the three graph types in a single figure"""
    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(24, 8))
    nx_graph = to_networkx(graph)
    nx_tree = to_networkx(tree)
    layout = circle_layout(graph)
    draw_heatmap_graph(nx_graph, layout, ax0, fig)
    draw_solution_tree_graph(nx_graph, nx_tree, layout, ax1, fig)
    draw_arc_sign_graph(nx_graph, layout, ax2, fig)
    plt.show()

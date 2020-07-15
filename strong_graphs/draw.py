import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import seaborn as sns
import math
from strong_graphs.data_structures.networks import to_networkx
import networkx as nx

# sorry simon
pi = 0.2
bendy_arcs = f"arc3, rad={pi}"

def circle_layout(graph):
    n = graph.number_of_nodes()
    frac = 2 * math.pi / n
    return {i: (-math.cos(i * frac), -math.sin(i * frac)) for i in graph.nodes()}

    # matplotlib.rcParams["mathtext.fontset"] = "custom"
    # matplotlib.rcParams["mathtext.rm"] = "Bitstream Vera Sans"
    # matplotlib.rcParams["mathtext.it"] = "Bitstream Vera Sans:italic"
    # matplotlib.rcParams["mathtext.bf"] = "Bitstream Vera Sans:bold"


def draw_graph_1(n, layout, ax, fig):
    weights = [w for _, _, w in n.edges.data("weight", default=None)]
    max_edge_abs = max(max(weights), -min(weights))
    norm = mpl.colors.Normalize(vmin=-max_edge_abs, vmax=max_edge_abs)
    cmap = mpl.cm.plasma
    nx.draw_networkx(
        n,
        node_color="xkcd:dark sky blue",
        pos=layout,
        with_labels=False,
        ax=ax,
        edge_color=[cmap(norm(x)) for x in weights],
        connectionstyle=bendy_arcs,
        edge_cmap=cmap,
    )
    fig.colorbar(
        mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
        ax=ax,
        orientation="horizontal",
        shrink=0.25,
        label="Arc Weight",
    )


def draw_graph_2(n, t, layout, ax, fig):
    nx.draw_networkx(
        n,
        node_color="xkcd:dark sky blue",
        pos=layout,
        ax=ax,
        edge_color="xkcd:light grey",
        connectionstyle=bendy_arcs,
    )
    nx.draw_networkx_edges(
        t, pos=layout, ax=ax, connectionstyle=bendy_arcs, edge_color="xkcd:red"
    )
    fig.colorbar(
        mpl.cm.ScalarMappable(cmap=mpl.cm.Oranges), ax=ax, orientation="horizontal", shrink=0.25,label='Arcs in Optimal Shortest Path'
    )


def draw_graph_3(n, layout, ax, fig):
    from palettable.cartocolors.diverging import Tropic_2

    # ax1.set_facecolor("k")
    #cmap = mpl.cm.get_cmap(Mendl_4.mpl_colormap, 2)
    cmap = ListedColormap(Tropic_2.mpl_colors)
    neg_colour = cmap(0)
    non_neg_colour = cmap(1)
    edge_colours = [
        neg_colour if w >= 0 else non_neg_colour
        for _, _, w in n.edges.data("weight", default=None)
    ]
    nx.draw_networkx(
        n,
        pos=layout,
        with_labels=False,
        node_color="xkcd:dark sky blue",
        edge_color=edge_colours,
        style="dashdot",
        connectionstyle=bendy_arcs,
    )
    #ax.legend(["negative", "non-negative"], loc=8)
    fig.colorbar(
        mpl.cm.ScalarMappable(cmap=cmap),
        ax=ax,
        orientation="horizontal",
        shrink=0.25,
        label='Negative vs Non-negative Arc weights'
    )  # , )

    plt.show()


def draw_graph(graph, tree, distances):
    fig, (ax0, ax1, ax2) = plt.subplots(1, 3, figsize=(24, 8))
    n = to_networkx(graph)
    t = to_networkx(tree)
    layout = circle_layout(graph)
    draw_graph_1(n, layout, ax0, fig)
    draw_graph_2(n, t, layout, ax1, fig)
    draw_graph_3(n, layout, ax2, fig)
    plt.show()

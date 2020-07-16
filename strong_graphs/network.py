from collections import defaultdict
import networkx as nx


class Network:
    """A network object that keeps track of both successors and predecessors"""

    def __init__(self, id=None):
        self.id = id
        self._nodes = set()  # {node_id: Node}
        self._arcs = dict()
        self._predecessors = defaultdict(set)
        self._successors = defaultdict(set)

    def __eq__(self, other):
        return self._nodes == other._nodes and self._arcs == other._arcs

    def add_node(self, node_id):
        assert node_id not in self._nodes, f"{node_id} already a node"
        self._nodes.add(node_id)
        return node_id

    def add_arc(self, u, v, w=0):
        assert u in self._nodes, f"{u} not a node"
        assert v in self._nodes, f"{v} not a node"
        assert u != v, f"no self loops {u} = {v}"
        assert (u, v) not in self._arcs.keys()
        self._arcs[(u, v)] = w
        self._predecessors[v].add((u, w))
        self._successors[u].add((v, w))

    def number_of_nodes(self):
        return len(self._nodes)

    def number_of_arcs(self):
        return len(self._arcs)

    def nodes(self):
        yield from self._nodes

    def arcs(self):
        for u, successors in self._successors.items():
            for v, w in successors:
                yield u, v, w

    def predecessors(self, node_id, with_weight=False):
        if with_weight:
            yield from self._predecessors[node_id]
        else:
            for pred_id, _ in self._predecessors[node_id]:
                yield pred_id

    def successors(self, node_id, with_weight=False):
        if with_weight:
            yield from self._successors[node_id]
        else:
            for succ_id, _ in self._successors[node_id]:
                yield succ_id


def to_networkx(graph):
    """For drawing purposes I just convert my graph to networkx"""
    n = nx.DiGraph()
    for node in graph.nodes():
        n.add_node(node)
    for (u, v, w) in graph.arcs():
        n.add_edge(u, v, weight=w)
    return n

from dataclasses import dataclass
from typing import Dict
from collections import defaultdict
import networkx as nx


class Network:
    def __init__(self, id=None):
        self.id = id
        self._nodes = set()  # {node_id: Node}
        self._arcs = dict()
        self._predecessors = defaultdict(set)
        self._successors = defaultdict(set)

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

    def replace_arc(self, u, v, w):
        assert (u, v) in self._arcs.keys()
        old_w = self._arcs[(u, v)]
        self._predecessors[v].discard((u, old_w))
        self._predecessors[v].add((u, w))
        self._successors[u].discard((v, old_w))
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


class SimpleNetwork:
    def __init__(self, id=None):
        self.id = id
        self.nodes = set()
        self._successors = defaultdict(set)

    def add_node(self, node_id):
        assert node_id not in self.nodes, f"{node_id} already a node"
        self.nodes.add(node_id)
        return node_id

    def add_arc(self, pred_id, succ_id, weight=0):
        assert pred_id in self.nodes, f"{pred_id} not a node"
        assert succ_id in self.nodes, f"{succ_id} not a node"
        self._successors[pred_id].add((succ_id, weight))

    def successors(self, node_id, with_weight=False):
        if with_weight:
            yield from self._successors[node_id]
        else:
            for succ_id, _ in self._successors[node_id]:
                yield succ_id


def from_networkx(directed_graph, network_type=Network):
    N = network_type()
    for node in directed_graph.nodes():
        N.add_node(node)
    for u, v, d in directed_graph.edges(data=True):
        N.add_arc(u, v, d["weight"])
    return N


def to_networkx(graph):
    n = nx.DiGraph()
    for node in graph.nodes():
        n.add_node(node)
    for (u, v, w) in graph.arcs():
        n.add_edge(u, v, weight=w)
    return n

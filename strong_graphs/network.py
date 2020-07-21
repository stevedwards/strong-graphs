import networkx as nx


class Network:
    """A network object that keeps track of both successors and predecessors"""

    def __init__(self, id=None):
        self.id = id
        self._arcs = dict()
        self._predecessors = {}
        self._successors = {}

    def __eq__(self, other):
        return (
            self._arcs == other._arcs and
            self._predecessors == other._predecessors and
            self._successors == other._successors
        )

    def add_node(self, node_id):
        assert node_id not in self._predecessors, f"{node_id} already a node"
        self._predecessors[node_id] = set()
        self._successors[node_id] = set()
        return node_id

    def add_arc(self, u, v, w=0):
        assert u in self._predecessors, f"{u} not a node"
        assert v in self._predecessors, f"{v} not a node"
        assert u != v, f"no self loops {u} = {v}"
        assert (u, v) not in self._arcs.keys(), f"Arc already exists {(u,v)=}"
        self._arcs[(u, v)] = w
        self._predecessors[v].add((u, w))
        self._successors[u].add((v, w))

    def number_of_nodes(self):
        return len(self._predecessors)

    def number_of_arcs(self):
        return len(self._arcs)

    def nodes(self):
        yield from self._predecessors

    def arcs(self):
        for u, successors in self._successors.items():
            for v, w in successors:
                yield u, v, w

    def predecessors(self, node_id):
        yield from self._predecessors[node_id]

    def successors(self, node_id):
        yield from self._successors[node_id]


def to_networkx(graph):
    """For drawing purposes I just convert my graph to networkx"""
    n = nx.DiGraph()
    for node in graph.nodes():
        n.add_node(node)
    for (u, v, w) in graph.arcs():
        n.add_edge(u, v, weight=w)
    return n

def negative_predecessors(graph):
    from collections import defaultdict

    my_dict = defaultdict(set)
    for u, v, w in graph.arcs():
        if w < 0:
            my_dict[v].add(u)
    return my_dict
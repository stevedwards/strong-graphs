from collections import defaultdict, deque


class DoublyLinkedTree:
    """
    Just a normal tree structure but where the parent nodes also keep track of the children
    """

    def __init__(self, root):
        self.root = root
        self._parent = defaultdict(lambda: None)
        self._children = defaultdict(set)

    def get_children(self, node):
        yield from self._children[node]

    def add(self, parent, child):
        self._parent[child] = parent
        self._children[parent].add(child)

    def remove(self, node):
        assert self._parent[node] is not None
        self._children[self._parent[node]].remove(node)
        self._parent[node] = None

    def contains(self, node):
        return self._parent[node] is not None or node == self.root

    def nodes(self):
        A = set(self._parent.keys())
        A.add(self.root[0])
        return A

    def arcs(self):
        for v, u in self._parent.items():
            yield (u, v, 0)

    def disassemble_subtree(self, source, target):
        """The most important part"""
        subtree_queue = deque([source])  # , maxlen=graph.number_of_nodes()
        to_unqueue = set()
        while subtree_queue:
            u = subtree_queue.popleft()
            for v in list(self.get_children(u)):
                self.remove(v)
                to_unqueue.add(v)
                if v == target:
                    return True, to_unqueue
                subtree_queue.append(v)
        return False, to_unqueue


class Tree:
    """
    Just a normal tree structure 
    """

    def __init__(self, root):
        self.root = root
        self._parent = defaultdict(lambda: None)

    def __contains__(self, node):
        return self._parent[node] is not None or node == self.root

    def add(self, parent, child):
        self._parent[child] = parent

    def remove(self, node):
        assert self._parent[node] is not None
        self._parent[node] = None
        

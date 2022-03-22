import numpy as np
import networkx as nx


class PhylogeneticTree:
    """Class for a phylogenetic tree specified by its leaf splits."""

    def __init__(self, splits, num_leaves):
        self.splits = splits
        self.num_leaves = num_leaves
        self.graph = self.generate_graph()

    def generate_graph(self):
        """Generate the graph object associated to the tree.
        This is done by starting with a star graph and inserting
        edges to match the given splits of the tree.
        """
        G = nx.Graph()
        for i in range(self.num_leaves):
            G.add_edge(i, self.num_leaves)
        for subset in self.splits:
            G = self._add_split(G, subset)
        return G

    def adjacency_matrix(self):
        """Adjacency matrix of the tree, as a dense np array."""
        return np.array(nx.adjacency_matrix(self.graph).todense())

    def leaf_nodes(self):
        """Nodes in the graph corresponding to leaves."""
        leaves = []
        for node in self.graph.nodes():
            if self.graph.degree(node) == 1:
                leaves += [node]
        return leaves

    def _add_split(self, G, subset):
        num_nodes = len(G.nodes())
        for v in range(self.num_leaves, num_nodes):
            compatible_edges = self._internal_vertex_compatible(G, subset, v)
            if compatible_edges:
                G.add_edge(num_nodes + 1, v)
                for e in compatible_edges:
                    G.remove_edge(*e)
                    other_node = next(x for x in e if x != v)
                    G.add_edge(other_node, num_nodes + 1)
        return G

    def _internal_vertex_compatible(self, G, subset, vertex):
        compatible_edges = []
        for edge in G.edges([vertex]):
            if self._edge_compatible(G, edge, subset, vertex):
                compatible_edges += [edge]
        if (
            len(compatible_edges) > 1
            and len(compatible_edges) < len(G.edges([vertex])) - 1
        ):
            return compatible_edges
        else:
            return False

    def _edge_compatible(self, G, edge, subset, vertex):
        H = G.copy()
        H.remove_edge(*edge)
        components = nx.connected_components(H)
        for c in components:
            if vertex not in c:
                separated = [v for v in c if v < self.num_leaves]
        if set(separated).issubset(set(subset)):
            return True
        else:
            return False

from dataclasses import dataclass
from typing import Optional, override

import networkx as nx
from matplotlib import pyplot as plt

from quark.protocols import Core

@dataclass
class MisGraphProvider(Core):
    """
    A module for creating random connected unweighted graphs for the MIS problem.

    :param nodes: The number of nodes in the graph
    :param seed: The seed for the random number generator
    """

    nodes: int = 10
    seed: int = 42

    @override
    def preprocess(self, data: None) -> None:
        self._graph = nx.newman_watts_strogatz_graph(self.nodes, 2, 0.75, self.seed)
        return self._graph


    @override
    def postprocess(self, data: Optional[list[int]]) -> Optional[float]:
        if data is None:
            print("No results found")
            return None

        for node in data:
            if any(self._graph.has_edge(node, other_node) for other_node in data):
                print("Result is not an independent set")
                return None

        self._result = data

        print(f"Size of the maximum independent set found: {len(data)}")
        return len(data)


    def visualize(self, path: str):
        node_colors = ["red" if node in self._result else "blue" for node in self._graph.nodes]
        nx.draw_circular(self._graph, node_color=node_colors, with_labels=True)
        plt.savefig(path)

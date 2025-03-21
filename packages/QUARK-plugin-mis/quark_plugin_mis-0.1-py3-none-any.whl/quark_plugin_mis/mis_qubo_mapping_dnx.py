from dataclasses import dataclass
from typing import Optional, override

import networkx as nx
import dwave_networkx as dnx

from quark.protocols import Core

@dataclass
class MisQuboMappingDnx(Core):
    """
    A module for mapping a graph to a QUBO formalism for the MIS problem
    """


    @override
    def preprocess(self, data: nx.Graph) -> dict:
        self._graph = data
        q = dnx.maximum_weighted_independent_set_qubo(data)
        return {"Q": q}


    @override
    def postprocess(self, data: dict) -> Optional[list[int]]:
        filtered_data = filter(lambda x: x[1] == 1, data.items())
        nodes = map(lambda x: x[0], filtered_data)
        return list(nodes)

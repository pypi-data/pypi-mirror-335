from dataclasses import dataclass
from typing import Optional, override

import networkx as nx

from quark.protocols import Core

@dataclass
class ClassicalMisSolver(Core):
    """
    Module for solving the MIS problem using a classical solver
    """


    @override
    def preprocess(self, data: nx.Graph) -> None:
        self._solution = nx.approximation.maximum_independent_set(data)


    @override
    def postprocess(self, data: None) -> Optional[list[int]]:
        return self._solution

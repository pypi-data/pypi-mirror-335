from dataclasses import dataclass
from typing import Optional, override

import networkx as nx

from quark.protocols import Core

@dataclass
class ClassicalTspSolver(Core):
    """
    Module for solving the TSP problem using a classical solver
    """


    @override
    def preprocess(self, data: nx.Graph) -> None:
        self._solution = nx.approximation.traveling_salesman_problem(data, cycle=False)


    @override
    def postprocess(self, data: None) -> Optional[list[int]]:
        return self._solution

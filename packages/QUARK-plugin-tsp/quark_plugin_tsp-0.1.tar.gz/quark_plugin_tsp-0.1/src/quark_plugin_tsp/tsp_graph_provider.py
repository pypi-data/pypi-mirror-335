from dataclasses import dataclass
from typing import Optional, override
import math

import networkx as nx

from quark.protocols import Core

@dataclass
class TspGraphProvider(Core):
    """
    A module for creating random weighted complete graphs for the TSP problem.

    :param nodes: The number of nodes in the graph
    :param seed: The seed for the random number generator
    """

    nodes: int = 10
    seed: int = 42


    @override
    def preprocess(self, data: None) -> nx.Graph:
        # Create a random graph without edges
        G = nx.random_geometric_graph(self.nodes, radius=0.0, seed=self.seed)
        pos = nx.get_node_attributes(G, "pos")

        # Add edges with weights equal to the Euclidean distance between the nodes
        for i in range(len(pos)):
            for j in range(i + 1, len(pos)):
                dist = math.hypot(pos[i][0] - pos[j][0], pos[i][1] - pos[j][1])
                G.add_edge(i, j, weight=dist)

        self._graph = G
        return self._graph


    @override
    def postprocess(self, data: Optional[list[int]]) -> Optional[float]:
        if data is None:
            print("No route found")
            return None

        if any(node not in data for node in self._graph.nodes()):
            print("Invalid route: Not all nodes were visited")
            return None
        print(f"All {len(self._graph.nodes())} nodes were visited")

        if len(data) != len(self._graph.nodes()):
            print("Invalid route: Some nodes were visited more than once")
            return None
        print("All nodes were visited exactly once")

        distance = 0
        node_id = data[0]
        for next_node_id in data[1:]:
            try:
                edge = self._graph[node_id][next_node_id]
            except KeyError:
                print(f"Invalid route: Edge {node_id} -> {next_node_id} does not exist")
                return None

            distance += edge["weight"]
            node_id = next_node_id

        print("Route found!")
        print(f"distance: {distance}")
        return distance

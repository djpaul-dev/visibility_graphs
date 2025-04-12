import math

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point

from polygon import Poly


class VisGraph:

    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.n = len(graph.nodes)
        self.m = len(graph.edges)

    @staticmethod
    def is_visible(polygon: Poly, i, j):
        v1, v2 = polygon.poly.exterior.coords[i], polygon.poly.exterior.coords[j]
        if v1 == v2:
            return False
        return polygon.poly.buffer(1e-9).contains(LineString([v1, v2]))

    def get_edge_orders(self):
        return sorted(
            [(k, v) for k, v in dict(self.graph.degree()).items()],
            key=lambda x: x[1],
            reverse=True,
        )

    def plot(self):
        pos = nx.get_node_attributes(self.graph, "pos")
        nx.draw(
            self.graph, pos, with_labels=True, node_color="lightblue", node_size=300
        )
        plt.gca().set_aspect("equal")
        plt.show()

    @staticmethod
    def from_poly(polygon: Poly):
        g = nx.Graph()
        vertices = polygon.poly.exterior.coords[:-1]

        for i, v in enumerate(vertices):
            g.add_node(i, pos=v)
            for j in range(i + 1, len(vertices)):
                if j == (i + 1) % len(vertices) or (i == 0 and j == len(vertices) - 1):
                    g.add_edge(i, j)
                elif VisGraph.is_visible(polygon, i, j):
                    g.add_edge(i, j)

        return VisGraph(g)

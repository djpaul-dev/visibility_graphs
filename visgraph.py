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
    def is_visible(polygon: Poly, v1, v2):
        if v1 == v2:
            return False

        l = LineString([v1, v2])
        if not polygon.poly.contains(l):
            return False

        for edge in zip(
            polygon.poly.exterior.coords[:-1], polygon.poly.exterior.coords[1:]
        ):
            if l.intersects(LineString(edge)):
                return False

        if l.intersects(
            LineString(
                [polygon.poly.exterior.coords[-1], polygon.poly.exterior.coords[0]]
            )
        ):
            return False

        return True

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
                if i == (j + 1) % len(vertices):
                    g.add_edge(i, j)
                elif VisGraph.is_visible(polygon, vertices[i], vertices[j]):
                    g.add_edge(i, j)

        return VisGraph(g)

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

    def construct_polygon(self):
        if self.n <= 2:
            return None

        degrees = self.get_edge_orders()

        if degrees[0][1] >= self.n:
            return None

        expected_vis = np.array([x[1] for x in degrees])
        curr_vis = np.array([2] * 3)

        if min(expected_vis) < 2:
            return None

        existing_edges = set([(0, 1), (0, 2), (1, 2)])  # make sure first < second
        valid_edges = set(existing_edges)
        if expected_vis[0] < 3:
            valid_edges.remove((0, 1))
            valid_edges.remove((0, 2))
        if expected_vis[1] < 3:
            valid_edges.remove((0, 1))
            valid_edges.remove((1, 2))
        if expected_vis[2] < 3:
            valid_edges.remove((1, 2))
            valid_edges.remove((0, 2))

        points = np.array([[-1, 0], [0, 1], [1, 0]])  # starting points
        points_idx = np.array([0, 1, 2])  # degrees[i] vertex is at points[points_idx[i]]
        for i in range(3, self.n):

            poly = Poly(Polygon(points))

            # no more valid edges to augment
            if len(valid_edges) == 0:
                return None

            # unfulfilled vertex in between fulfilled vertices
            vis_diff = expected_vis[:i] - curr_vis
            padded = np.pad(vis_diff, 1, mode="wrap")
            if (
                len(
                    np.where(
                        (padded[1:-1] != 0) & (padded[:-2] == 0) & (padded[2:] == 0)
                    )[0]
                )
                == 0
            ):
                return None

            # closest vertex to fulfillment
            valid_edges_lst = list(valid_edges)
            edge_scores = [min(vis_diff[i], vis_diff[j]) for i, j in valid_edges_lst if vis_diff[i] != 0 and vis_diff[j] != 0 else float("inf")]
            for e in valid_edges_lst[np.argsort(edge_scores)]: 
                # find point to place new vertex
                new_pt = [0, 0] # TODO
                found = True
                fulfillment_incs = [e[0], e[1]]
                for j, v in enumerate(vis_diff):
                    if v == 0 and poly.polygon.buffer(1e-9).contains(LineString([new_pt, points[points_idx[j]]])):
                        found = False
                        break
                    elif v > 0 and poly.polygon.buffer(1e-9).contains(LineString([new_pt, points[points_idx[j]]])):
                        fulfillment_incs.append(j)
                if found:
                    points = np.insert(points, i, new_pt, axis=0)
                    points_idx[points_idx > i] += 1
                    points_idx.append(i)
                    for j in fulfillment_incs:
                        curr_vis[j] += 1
                    vis_diff = expected_vis[:i] - curr_vis
                    for e2 in valid_edges:
                        if vis_diff[e2[0]] == 0 or vis_diff[e2[1]] == 0:
                            valid_edges.remove(e2)

                    break
            

            
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

import matplotlib.pyplot as plt
import networkx as nx

from visgraph import VisGraph
from polygon import Poly


def plot(polygon: Poly, graph: VisGraph):
    g = graph.graph
    pos = nx.get_node_attributes(g, "pos")

    # Plot the polygon boundary
    x, y = polygon.poly.exterior.xy
    plt.plot(x, y, "k-", linewidth=2, label="Polygon Boundary")

    # Plot the visibility graph
    nx.draw(
        g,
        pos,
        with_labels=True,
        labels={i: str(i) for i in g.nodes},
        node_color="skyblue",
        node_size=100,
        edge_color="orange",
        width=1,
    )

    plt.gca().set_aspect("equal")
    print(g.edges)
    print(graph.get_edge_orders())
    plt.show()


if __name__ == "__main__":
    iters = 100
    for i in range(iters):
        p = Poly.random(10)
        vg = VisGraph.from_poly(p)
        print([x[1] for x in vg.get_edge_orders()])
    plot(p, vg)

    # plot(p, vg)
    # vg.plot()

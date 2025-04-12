from visgraph import VisGraph
from polygon import Poly

if __name__ == "__main__":
    p = Poly.random(10)
    vg = VisGraph.from_poly(p)

    # vg.plot()
    p.plot()

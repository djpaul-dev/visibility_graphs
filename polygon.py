import random
import math
from itertools import combinations

from shapely.geometry import Polygon, LineString, Point
import numpy as np
import matplotlib.pyplot as plt


class Poly:

    def __init__(self, polygon: Polygon):
        self.poly = polygon
        self.points = np.array(self.poly.exterior.coords)
        self.n = len(self.points)

    def plot(self):
        x, y = self.poly.exterior.xy
        plt.plot(x, y, "k-", linewidth=2, label="Polygon Boundary")
        plt.show()

    @staticmethod
    def closest_dist(points):
        return min(math.dist(p1, p2) for p1, p2 in combinations(points, 2))

    @staticmethod
    def random(n, radius=1):

        points = None

        while points is None or Poly.closest_dist(points) < 1e-9:
            points = []
            angles = sorted([random.uniform(0, 2 * math.pi) for _ in range(n)])
            for a in angles:
                r = random.uniform(-1, 1)
                points.append((math.cos(a) * (radius + r), math.sin(a) * (radius + r)))

        return Poly(Polygon(points))

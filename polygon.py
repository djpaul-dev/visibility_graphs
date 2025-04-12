import random
import math

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
    def random(n, radius=1):
        angles = sorted([random.uniform(0, 2 * math.pi) for _ in range(n)])
        print(angles)
        points = []
        for a in angles:
            r = random.uniform(-1, 1)
            points.append((math.cos(a) * (radius + r), math.sin(a) * (radius + r)))

        print(points)
        return Poly(Polygon(points))

from shapely.geometry import MultiPoint, Point, Polygon
import pandas as pd
import numpy as np
import math

def toCartesian(latitude, longitude):
    x = longitude * 70_800
    y = latitude * 111_300
    return Point(x, y)

def get_locality(points):
    mp = MultiPoint(points)
    rect = mp.minimum_rotated_rectangle
    if rect.geom_type != "Polygon":
        return 0
    v = list(rect.exterior.coords)
    a = Point(v[0]).distance(Point(v[1]))
    b = Point(v[1]).distance(Point(v[2]))
    return max(a, b)


def xrolling(array, presize, postsize, func):
    n = len(array)
    result = np.full(n, np.nan)
    for i in range(presize, n-postsize):
        result[i] = func(array[i-presize:i+postsize+1])
    return result

df = pd.read_csv("data/onesec_all.csv")
points = [toCartesian(row["locLat"], row["locLon"]) for _, row in df.iterrows()]
print("hotovo")
lr = xrolling(points, 5, 5, get_locality)
df["locality"] = lr
df.to_csv("data/onesec_all_02_locality10.csv")
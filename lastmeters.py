import sys

import pandas as pd
import datetime

from matplotlib import ticker
from shapely.geometry import Point
import matplotlib.pyplot as plt

points = [(50.52941, 14.0719), (50.52927, 14.0722)]

def toCartesian(latitude, longitude):
    x = longitude * 70_800
    y = latitude * 111_300
    return Point(x, y)


def get_path(pathdata, starttime, endtime):
    return pathdata[(starttime <= pathdata["timestamp_m"]) &  (pathdata["timestamp_m"] <= endtime)]


def minimal_distance(path, lat, long):
    p = toCartesian(lat, long)
    minimal = path.apply(lambda x: toCartesian(x["locLat"], x["locLon"]).distance(p),
                         axis=1)
    return minimal.min(), minimal.idxmin()

routes = pd.read_csv("data/localized_routes_01.csv")
pathdata = pd.read_csv("data/01_2021-02-25.csv",
                       index_col="beat",
                       converters={
                           "beat": lambda x: int(float(x)),
                           "timestamp_m": lambda x: int(float(x))})
pathdata2 = pd.read_csv("data/01_2021-03-16.csv",
                       index_col="beat",
                       converters={
                           "beat": lambda x: int(float(x)),
                           "timestamp_m": lambda x: int(float(x))})
pathdata = pathdata.append(pathdata2)
routes["date"] = pd.to_datetime(routes["beat"], unit="s")
routes = routes[(datetime.datetime(2021,2,25) <= routes["date"])
                & (routes["date"] <= datetime.datetime(2021,2,26))
                |
                (datetime.datetime(2021, 3, 16) <= routes["date"])
                & (routes["date"] <= datetime.datetime(2021, 3, 17))]
print(routes)

p1_dist = []
p2_dist = []
start_beat = []
p1_beat = []
p2_beat = []
end_beat = []
t1_longs = []
t1_lats = []
t1_plongs = []
t1_plats = []
t2_longs = []
t2_lats = []
t2_plongs = []
t2_plats = []
t3_longs = []
t3_lats = []
t3_plongs = []
t3_plats = []
results = []


for index, route in routes.iterrows():
    starttime = route["beat"]
    endtime = route["end_beat"]
    path = get_path(pathdata, starttime * 1000,  endtime * 1000)
    if len(path) == 0:
        continue
    start_beat.append(path.index[0])
    end_beat.append(path.index[-1])
    dist1, idx1 = minimal_distance(path, *points[0])
    p1_dist.append(dist1)
    p1_beat.append(idx1)
    dist2, idx2 = minimal_distance(path, *points[1])
    p2_dist.append(dist2)
    p2_beat.append(idx2)
    if dist1 < 7.0:
        if route["locLon_end"] > 14.0726 and route["locLat_end"] > 50.5291:
            t1_plats.extend(path["locLat"])
            t1_plongs.extend(path["locLon"])
            t1_lats.append(route["locLat_end"])
            t1_longs.append(route["locLon_end"])
            results.append(0)
        elif route["locLon_end"] > 14.07265:
            t3_plats.extend(path["locLat"])
            t3_plongs.extend(path["locLon"])
            t3_lats.append(route["locLat_end"])
            t3_longs.append(route["locLon_end"])
            results.append(2)
        else:
            t2_plats.extend(path["locLat"])
            t2_plongs.extend(path["locLon"])
            t2_lats.append(route["locLat_end"])
            t2_longs.append(route["locLon_end"])
            results.append(1)
    else:
        results.append(-1)

plt.scatter(t2_plongs, t2_plats, c="#9999FF", s=1)
plt.scatter(t1_plongs, t1_plats, c="#99FF99", s=1)
plt.scatter(t3_plongs, t3_plats, c="#FF9999", s=1)
plt.scatter(t1_longs, t1_lats, c="#00AA00")
plt.scatter(t2_longs, t2_lats, c="#0000AA")
plt.scatter(t3_longs, t3_lats, c="#AA0000")
plt.scatter([points[0][1]], [points[0][0]], s=5, c="k")
#plt.scatter([points[1][1]], [points[1][0]], c="r")
plt.gca().xaxis.set_minor_locator(ticker.MultipleLocator(0.0001))
plt.gca().yaxis.set_minor_locator(ticker.MultipleLocator(0.0001))
plt.grid(True, which="both")
plt.show()
routes["p1_minimal_dist"] = p1_dist
routes["p2_minimal_dist"] = p2_dist
routes["start_pbeat"] = start_beat
routes["p1_pbeat"] = p1_beat
routes["p2_pbeat"] = p2_beat
routes["end_pbeat"] = end_beat
routes["target"] = results

routes.to_csv("data/routes_pdist_brezen_01.csv")

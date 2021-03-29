import json
from shapely.geometry import Polygon, Point
import matplotlib.pyplot as plt
import geopandas as gpd
import pandas as pd
import numpy as np


def parse_point(position):
    long, lat = position.split(",")
    return float(long), float(lat)


class NPolygon:
    def __init__(self, shapely_polygon, name, type):
        self.polygon = shapely_polygon
        self.name = name
        self.type = type

    def __str__(self):
        return f"{self.name}[{self.type}]"

    def plot(self):
        plt.plot(self.polygon.exterior.xy)


def getposition(lat, lon, npolygons):
    detail= np.empty(lat.shape, dtype=np.object)
    type = np.empty(lat.shape, dtype=np.object)
    for i, v in lat.iteritems():
        if isinstance(lat[i], float):
            point = Point(lon[i], lat[i])
        else:
            point = Point(lon[i].iloc[0], lat[i].iloc[0])
        for p in npolygons:
            if p.polygon.contains(point):
                detail[i] = p.name
                type[i] = p.type
    return detail, type

with open("data/polygon_data json") as f:
    polygons = json.load(f)
    npolygons = []
    for spolygon in polygons:
        if "coordinates" not in spolygon:
            continue
        name = spolygon["name"]
        polygon = Polygon([parse_point(position) for position in spolygon["coordinates"].split(";")
                           if position])
        type = spolygon["typeData"]
        npolygons.append(NPolygon(polygon, name, type))

#p = gpd.GeoSeries(p.polygon for p in npolygons)
#p.plot()
#plt.show()

suffix = "_01"

routes = pd.read_csv(f"data/routes{suffix}.csv", converters={"beat": lambda x: int(float(x))},
                     usecols=["beat", "end_beat"])
print(routes)
positions = pd.read_csv(f"data/onesec_all{suffix}.csv", converters={"beat": lambda x: int(float(x))},
                        usecols=["beat", "locLat", "locLon"])
positions = positions.set_index("beat")

jdf = routes.join(positions, on="beat").join(positions, on="end_beat", rsuffix="_end", lsuffix="_start")

jdf["start"], jdf["start_type"] = getposition(jdf["locLat_start"], jdf["locLon_start"], npolygons)
jdf["end"], jdf["end_type"] = getposition(jdf["locLat_end"], jdf["locLon_end"], npolygons)

print(jdf)
jdf.to_csv(f"data/localized_routes{suffix}.csv")
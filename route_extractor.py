import glob
import pandas as pd
from shapely.geometry import Point
from matplotlib.pyplot import show

def toCartesian(latitude, longitude):
    x = longitude * 70_800
    y = latitude * 111_300
    return Point(x, y)

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 10)
routes = []

df = pd.read_csv("data/onesec_all_01.csv")
df["horizontalDistance"] = df["horizontalDistance"].rolling(window=5).mean()
enroute = False
for i in range(len(df)):
    dist = df.loc[i, "horizontalDistance"]
    time = df.loc[i, "timestamp_m"]
    if dist > 0 and not enroute:
        start = time
        startbeat = df.loc[i, "beat"]
        startpoint = toCartesian(latitude=df.loc[i, "locLat"], longitude=df.loc[i, "locLon"])
        enroute = True
    if dist == 0 and enroute:
        end = time
        endbeat = df.loc[i, "beat"]
        duration = (end-start)/1000
        endpoint = toCartesian(latitude=df.loc[i, "locLat"], longitude=df.loc[i, "locLon"])
        dst = endpoint.distance(startpoint)
        if 8  < duration < 200 and dst > 10:
            routes.append((int(startbeat), int(endbeat), int(duration+0.5), dst))
        enroute = False

df = pd.DataFrame(routes, columns=["beat", "end_beat",  "duration", "se_distance"])
df.set_index(["beat"])
df.hist("duration", bins=25)
print(df.info())
show()
df.to_csv("data/routes_01.csv")

import glob
import hashlib
import pathlib
import random
import numpy as np
import pandas as pd
from shapely.geometry import MultiPoint, Point
import pickle
from manip_detection import preprocess_hdist


def cached(enable, prefix=""):
    def decorator(f):
        def wrapper(*args, **kwargs):
            hash = hashlib.sha1(",".join(repr(p) for p in args).encode(encoding="utf8")).hexdigest()
            cache_file = pathlib.Path(f"{prefix}{hash}.plk")
            if enable and cache_file.exists():
                print(f"read from cache {cache_file}")
                with open(cache_file, "rb") as input:
                    return pickle.load(input)
            retval = f(*args, **kwargs)
            print(f"write to cache {cache_file}")
            with open(cache_file, "wb") as output:
                pickle.dump(retval, output)
            return retval
        return wrapper
    return decorator


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


class WindowPicker:
    def __init__(self, filenames):
        filenames = list(filenames)
        self.id = ":".join(filenames)
        hash = hashlib.sha1(self.id.encode(encoding="utf8")).hexdigest()
        cache = pathlib.Path(f"{hash}.plk")
        if cache.exists():
            self.df = pd.read_pickle(cache)
        else:
            self.df = pd.concat([pd.read_csv(file) for file in sorted(filenames)])
            self.df = self.df.astype({"beat": np.int, "timestamp_m": np.int})
            self.df["used"] = np.zeros(len(self.df), dtype=np.int8)
            self.df.to_pickle(cache)

    def __repr__(self):
        return self.id

    def random_data(self, size, attrib, testSet=False):
        indexes = self.random_pick(size, testSet)
        return self.df.iloc[indexes][attrib]

    def random_pick(self, size, testSet=False):
        n = len(self.df)
        while True:
            i = random.randint(0, n-size)
            if testSet and self.df.iloc[i:i+size]["used"].sum() > 0:
                continue
            subdf = self.df.iloc[i:i+size,  0]
            diff = subdf.iloc[1:].to_numpy() - subdf.iloc[:-1].to_numpy()
            if np.all(diff == 1):
                indices = np.arange(i, i+size)
                self.df.iloc[indices, 15] += 1
                return indices


def labelCommon(df: pd.DataFrame):
    manips = df["horizontalDistance"].to_numpy()
    m = np.any(np.abs(manips) == 2)
    return 1.0 if m else 0.0


@cached(True, "sample_")
def populate(picker, size, interval, attribs, testSet=False):
    data = np.empty((size, interval, len(attribs)), dtype=np.float32)
    localities = np.empty((size, 1), dtype=np.float32)
    labels = np.empty((size, 1), dtype=np.float32)
    for i in range(size):
        while True:
            sample = picker.random_data(interval, attribs + ["horizontalDistance", "locLat", "locLon"], testSet)
            label = np.array(labelCommon(sample))
            if label.sum() == 0: # no manipulation
                if random.uniform(0, 1) > 0.33:
                    continue
            points = [toCartesian(row["locLat"], row["locLon"]) for _, row in sample.iterrows()]
            loc = get_locality(points)
            data[i] = sample.to_numpy()[:, :-3]
            localities[i] = loc
            labels[i] = label
            break
    return data, localities, labels


if __name__ == "__main__":
   pd.set_option('display.max_rows', 500)
   picker = WindowPicker(glob.glob("../data/01_2020*.csv"))
   picker.df["accX"] = picker.df["horizontalDistance"]
   picker.df["horizontalDistance"] = preprocess_hdist(picker.df, unload_limit=3000, load_limit=3000)
   data, localities, labels = populate(picker, 1000, 200, ["accX"])
   rdf = pd.DataFrame({"locality": localities.flatten(), "label": labels.flatten()})
   rdf.to_csv("windows.csv")



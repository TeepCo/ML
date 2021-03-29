import pandas as pd
import glob
import numpy as np


def preprocess_hdist(df: pd.DataFrame, load_limit, unload_limit) -> np.ndarray:
    data = df[["timestamp_m", "horizontalDistance"]].copy()
    distances = (data["horizontalDistance"] > 0).astype(np.int).to_numpy()
    diff = distances[1:] - distances[:-1]

    lasttime = 0
    lastindex = 0
    for i in range(len(diff)):
        if diff[i] != 0:
            time = data.iloc[i]["timestamp_m"]
            if time - lasttime < unload_limit and diff[i] == 1:
                diff[lastindex] = 0
                diff[i] = 0
            lastindex = i
            lasttime = time

    lasttime = 0
    lastindex = 0
    for i in range(len(diff)):
        if diff[i] != 0:
            time = data.iloc[i]["timestamp_m"]
            if time - lasttime > load_limit and diff[i] == -1:
                diff[lastindex] *= 2
                diff[i] *= 2
            lastindex = i
            lasttime = time

    return np.append(diff, 0)
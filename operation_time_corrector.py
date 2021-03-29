import pandas as pd
import numpy as np
import math


def wfunc(w, i, threshold):
    min = np.nanmin(w)
    max = np.nanmax(w)
    if max - min < threshold:
        return np.nanmean(w)
    mid = (max+min)/2
    with np.errstate(invalid='ignore'):
        smaller = np.where(w <= mid)[0]
        bigger = np.where(w > mid)[0]
    if np.all(i > smaller) and np.any(bigger <= i) or np.all(i < smaller) and np.any(bigger >= i):
        return np.nanmean(w[bigger])
    if np.all(i > bigger) and np.any(smaller <= i) or np.all(i < bigger) and np.any(smaller >= i):
        return np.nanmean(w[smaller])
    return math.nan

def windowing(v, wfunc, before = 1, after = 1):
    size = v.shape[0]
    assert before + after + 1 <= size, "Small array fow window"
    r = np.empty_like(v)
    for i in range(size):
        start = i - before
        end = i + after
        if start < 0:
            end -= start
            start = 0
        if end > size - 1:
            start -= end - size + 1
            end = size - 1
        r[i] = wfunc(v[start:end+1], i-start)
    return r

df = pd.read_csv("data/operaceDEV01.csv")
df["t_diff"] = (df["cas_server"] - df["cas_klient"]) / 1_000
df.loc[df['t_diff'] > 60 * 30, 't_diff'] = np.nan
r = windowing(df["t_diff"].astype(np.float64).to_numpy(), lambda w, i: wfunc(w, i, 10), 7, 7)
df["corr_t_diff"] = np.round(r, 2)
df["cas_real"] = df["cas_klient"] + (df["corr_t_diff"] * 1_000).astype(np.int)
print(df)
df.to_csv("data/operaceDEV01_corr.csv")
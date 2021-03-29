import pandas as pd
from shapely.geometry import Point
import numpy as np
import math

def toCartesian(latitude, longitude):
    x = longitude * 70_800
    y = latitude * 111_300
    return Point(x, y)

operace = pd.read_csv("data/operaceDEV01_corr.csv")
presuny = pd.read_csv("data/routes_01.csv")
polohy = pd.read_csv("data/onesec_all_01.csv")


def poloha(time):
    near_index = polohy['beat'].sub(time).abs().idxmin()
    return toCartesian(polohy.iloc[near_index]["locLat"], polohy.iloc[near_index]["locLon"])

j = 0
jizda = np.full(len(operace), math.nan)
prev_vykladka = np.full(len(operace), math.nan)
next_nakladka = np.full(len(operace), math.nan)
prev_nakladka = np.full(len(operace), math.nan)
next_vykladka = np.full(len(operace), math.nan)
d_next_nakladka = np.full(len(operace), math.nan)
d_prev_nakladka = np.full(len(operace), math.nan)

for i in range(len(operace)):
    otime = int(operace.iloc[i]["cas_real"] / 1_000 + 0.5)
    opoloha = poloha(otime)
    while True:
        if j == len(presuny):
           break
        if j == 0:
            t0 = presuny.iloc[0]["beat"] - 120
        else:
            t0 = presuny.iloc[j-1]["end_beat"]
        poloha0 = poloha(t0)
        t1 = presuny.iloc[j]["beat"]
        poloha1 = poloha(t1)
        t2 = presuny.iloc[j]["end_beat"]
        poloha2 = poloha(t2)
        if t0 <= otime <= t1:
            if t1-otime < 300:
                jizda[i] = j
                prev_vykladka[i] = t0 - otime
                next_nakladka[i] = t1 - otime
                d_next_nakladka[i] = opoloha.distance(poloha1)
                print(f"OK:  {otime-t0} - {t1-otime} [{opoloha.distance(poloha1)}] {i}/{j}")
            break
        if t1 <= otime <= t2:
            if t2-otime < 300:
                jizda[i] = j
                prev_nakladka[i] = t1 - otime
                next_vykladka[i] = t2 - otime
                d_prev_nakladka[i] = opoloha.distance(poloha1)
                print(f"--- {otime-t1} [{opoloha.distance(poloha1)}] - {t2-otime} [{opoloha.distance(poloha2)}]  {i}/{j}")
            break
        j += 1
operace["jizda"] = jizda
operace["prev_vykladka_dt"] = prev_vykladka
operace["next_nakladka_dt"] = next_nakladka
operace["prev_nakladka_dt"] = prev_nakladka
operace["next_vykladka_dt"] = next_vykladka
operace["next_nakladka_vzdalenost"] = d_next_nakladka
operace["prev_nakladka_vzdalenost"] = d_prev_nakladka
operace.to_csv("data/operaceDEV01_s_jizdami.csv")
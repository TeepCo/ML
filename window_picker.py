import pandas as pd
import numpy as np
import glob
import hashlib
import pathlib
import random
import seaborn
import matplotlib.pyplot as plt

class WindowPicker:
    def __init__(self, filenames):
        filenames = list(filenames)
        hash = hashlib.sha1("".join(filenames).encode(encoding="utf8")).hexdigest()
        cache = pathlib.Path(f"{hash}.plk")
        if cache.exists():
            self.df = pd.read_pickle(cache)
        else:
            self.df = pd.concat([pd.read_csv(file) for file in sorted(filenames)])
            self.df = self.df.astype({"beat": np.int, "timestamp_m": np.int})
            self.df.to_pickle(cache)

    def random_pick(self, size):
        n = len(self.df)
        while True:
            i = random.randint(0, n-size)
            subdf = self.df.iloc[i:i+size,  0]
            diff = subdf.iloc[1:].to_numpy() - subdf.iloc[:-1].to_numpy()
            if np.all(diff == 1):
                return np.arange(i, i+size)


picker = WindowPicker(glob.glob("data/02_2020*.csv"))
print(picker.random_pick(5))

print(picker.df.info())

print(picker.df["accY"].mean()/picker.df["accZ"].mean())

# picker.df.to_csv("all_02.csv")

#mdf = picker.df.loc[:, ["accX", "accY", "accZ"]].melt(var_name="column", value_name="val")
#seaborn.violinplot(x="column", y="val", data=mdf)
#plt.grid(True)
#plt.show()

#mdf = picker.df.loc[:, ["gyroX", "gyroY", "gyroZ"]].melt(var_name="column", value_name="val")
#seaborn.violinplot(x="column", y="val", data=mdf)
#plt.grid(True)
#plt.show()

#mdf = picker.df.loc[:, ["uncMagX", "uncMagY", "unMagZ"]].melt(var_name="column", value_name="val")
#seaborn.violinplot(x="column", y="val", data=mdf)
#plt.grid(True)
#plt.show()


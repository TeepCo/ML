import glob
import  pandas as pd

df = pd.concat([pd.read_csv(file) for file in sorted(glob.glob("data/onesec_01_*.csv"))])
df.to_csv("data/onesec_all_01.csv")


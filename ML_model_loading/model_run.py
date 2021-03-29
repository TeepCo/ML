import numpy as np
from data_picker import populate, WindowPicker
import settings
import glob
from model import VAL_SPLIT, EPOCHS, mixed_model
import pandas as pd
from sklearn.metrics import confusion_matrix
from manip_detection import preprocess_hdist
import sys

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

# příprava trénovacích dat
picker = WindowPicker(glob.glob("../data/02_2020*.csv"))
df = picker.df
df["d_uncMagX"] = df["uncMagX"].diff() # data magnetometru jsou nahrazena derivací (aby nezávisela na absolutní pozici)
df["d_uncMagY"] = df["uncMagY"].diff()
df["d_uncMagZ"] = df["unMagZ"].diff()
df["accZ"] += 10  # normalizace gravitace (střední hodnota accZ je tak blízká 0)
# přeškálování hodnot gyroskopu
df["gyroX"] *= 10
df["gyroY"] *= 10
df["gyroZ"] *= 10
# a čidel vzdálenosti (formálně z cm na m)
df["horizontalDistance"] *= 0.01
df["verticalDistance"] *= 0.01

df["horizontalDistance"] = preprocess_hdist(df, unload_limit=3000, load_limit=3000)
df.fillna(method="bfill", inplace=True)  # nahrazení null hodnot (vzniká jako výsledek diff)

NUMBER_OF_WINDOW_TRAINING = 5000  # může se až tak na 20000 (pak už nejsou data)

X_train, X2_train, y_train = populate(picker, NUMBER_OF_WINDOW_TRAINING, settings.WINDOW_SIZE, settings.ATTRIB)

h, _ = np.histogram(y_train, bins=2)
print(h)  # vypisuje podíl

model = mixed_model() # nahrání modelu

history = model.fit([X_train, X2_train], y_train, validation_split=VAL_SPLIT,
                    epochs=EPOCHS, shuffle=False)

# ověření na testovacích datech

X_test, X2_test, y_test = populate(picker, 1000, settings.WINDOW_SIZE, settings.ATTRIB, testSet=True)
y_test = y_test.astype(np.int32)
y_pred = model.predict([X_test, X2_test])  # predikace podle naučeného modelu
y_pred = (y_pred > 0.5).astype(np.int32)  # hodnoty nad 0.5 jsou interpretovány jako predikce manipulace

tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel() # vytváření matici nejistoty
print(f"true negative: {tn}, false positive: {fp}, false negative: {fn}, true positive {tp}")




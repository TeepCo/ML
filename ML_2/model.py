import glob
import itertools
import sys
from itertools import product
from pickle import dump

from keras.layers import Input, Dense
from keras.models import Sequential
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import RepeatedKFold
import numpy as np
from keras.utils import to_categorical

from loader import Picker
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt

names = np.array(["near left", "near right", "far right"])


def get_model(inputs, outputs):
    model = Sequential()
    model.add(Dense(100,  input_dim=inputs, activation="relu"))
    model.add(Dense(20, input_dim=inputs, activation="relu"))
    model.add(Dense(outputs, activation="softmax"))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def evaluate(X_train, y_train, X_test, y_test, targets):
    n_inputs, n_outputs = X_train.shape[1], y_train.shape[1]
    model = get_model(n_inputs, n_outputs)
    model.fit(X_train, y_train, epochs=15, verbose=0)
    yhat = model.predict(X_test)
    yhat = yhat.round()
    acc = accuracy_score(y_test, yhat)
    cm = confusion_matrix(y_test.argmax(1), yhat.argmax(1)) # urci matici zamen
    #if n_outputs == 2:
    #    tn, fp, fn, tp = cm.ravel()  # dle dokumentace POZOR, je to otocene vuci bezne notaci
    #   print(f"true negative: {tn}, false positive: {fp}, false negative: {fn}, true positive {tp}")
    return acc, cm


def draw_matrix(cm, targets):
    df_cm = pd.DataFrame(cm, index=names[targets], columns=names[targets])
    sn.heatmap(df_cm, annot=True, cbar=False, cmap="YlGnBu")
    plt.show()


def get_samples(p, n):
    i, X = p.pick()
    y = to_categorical(i, num_classes=len(targets))
    for _ in range(n - 1):
        i, x = p.pick()
        X = np.vstack((X, x))
        y = np.vstack((y, to_categorical(i, num_classes=len(targets))))
    return X, y


train_samples = 20
test_samples = 10
targets = [0, 1]
reps = 20

groups = []
for i in targets:
    groups.append(glob.glob(f"../data/signals/{i}_*SAMPLE*.csv"))

s = ["accX", "accY", "accZ", "gyroX", "gyroY", "gyroZ", "d_uncMagX", "d_uncMagY", "d_uncMagZ"]
results = {}
for senzors in itertools.chain([[item] for item in s],
                               [["accZ", "d_uncMagZ"], ["accX", "gyroZ"]]):
    print(senzors)

    summ_acc = 0
    sum_cm = np.zeros((2,2), dtype=np.float64)
    for _ in range(reps):
        while True:
            try:
                p = Picker(groups, senzors, 79)
                X_train, y_train = get_samples(p, train_samples)
                X_test, y_test = get_samples(p, test_samples)
                acc, cm = evaluate(X_train, y_train, X_test, y_test, targets)
                summ_acc += acc
                sum_cm += cm
                break
            except IndexError:
                continue
    results[tuple(senzors)] = dict(acc=summ_acc / reps, cm=sum_cm / reps)

print(results)
with open("ml1b.dump", "wb") as f:
    dump(results, f)


import glob
from copy import deepcopy

import pandas as pd
from random import uniform, choice
import numpy as np


def random_pick(probabilities, groups):
    n = len(probabilities)
    p = np.array(probabilities)
    s = np.sum(probabilities)

    p = np.cumsum(p)
    p = p / s
    x = uniform(0, 1)
    for i in range(n):
        if x <= p[i]:
            if not groups[i]:
                raise IndexError(f"Group {i} exhausted")
            return i, choice(groups[i])


def get_input(filename, attributes, rightindex):
    df = pd.read_csv(filename).loc[0:rightindex, attributes]
    r = df.to_numpy()
    return r.reshape(r.shape[0] * r.shape[1])


class Picker:
    def __init__(self, groups, attributes, right_index, probabilities=None):
        self.groups = deepcopy(groups)
        self.attrs = attributes
        self.rindex = right_index
        n = len(groups)
        if probabilities is not None:
            self.prob = np.array(probabilities)
        else:
            n = len(self.groups)
            self.prob = np.ones(n) / n

    def pick(self):
        i, file = random_pick(self.prob, self.groups)
        self.groups[i].remove(file)
        return i, get_input(file, self.attrs, self.rindex)

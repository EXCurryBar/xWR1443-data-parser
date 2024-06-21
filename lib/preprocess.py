import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import measurements

DELAY = 15
BINS = 50


def cosine_similarity(vector1, vector2):
    v1 = np.array(vector1)
    v2 = np.array(vector2)

    dot_product = np.dot(v1, v2)

    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    return dot_product / (norm1 * norm2)


class Preprocess:
    def __init__(self):
        self.count = 0
        self.previous_vector = None

    def load_group_by_subject(self, groups, vectors):
        similarity = list()
        if len(vectors) == 1 or self.previous_vector is None:
            self.previous_vector = vectors[0]
            index = 0
        elif len(vectors) > 1:
            similarity = [cosine_similarity(self.previous_vector, item) for item in vectors]
            index = max(range(len(similarity)), key=lambda i: abs(similarity[i]))
        else:
            index = 0
        group_transpose = np.array(groups[index]).T
        xs = group_transpose[0]
        ys = group_transpose[1]
        data, qx, qy = np.histogram2d(xs, ys, bins=BINS, range=np.array([(-2, 2), (1, 4)]))
        return data.reshape((BINS, BINS, -1))
        # return plt.pcolormesh(qx, qy, data)

    def generare_graph(self) -> list:
        all_graphs = list()
        for name in self.subject:
            subject = name.split('/')[-1]
            print(subject)
            targets = [folder for folder in self.subject_path if name in folder]
            for target in targets:
                self._load_group_by_subject(target)

    def run(self):
        self.generare_graph()


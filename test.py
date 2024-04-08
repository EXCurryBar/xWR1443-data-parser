import json
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
# import sounddevice


data = json.load(open("output_file/test1.json", 'r'))
entropy_list_x = list()
entropy_list_y = list()
delay = 15
bins = 25
# prev = np.ndarray((bins, bins))
list_of_entropy = list()
list_of_x = list()
list_of_y = list()
list_of_atan = list()
for i in range(len(data)):
    xs = list()
    ys = list()
    pca = PCA(n_components=2)
    # for _ in range(start_index, i):
    for g in data[i][1].get("group", []):
        group = np.array(g)
        group_transpose = group.T
        xs += list(group_transpose[0])
        ys += list(group_transpose[1])
        h, q_x, q_y = np.histogram2d(xs, ys, bins=bins, range=np.array([(-3, 3), (-3, 3)]))


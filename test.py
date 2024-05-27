import json
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np


data = json.load(open("output_file/test02_light_fall_lr_0.json", 'r'))
delay = 15
bins = 25

origin = [0], [0]
previous_vector = list()
for i in range(len(data)):
    xs = list()
    ys = list()
    pca = PCA(n_components=2)
    group_vector_mse = list()
    group_vector_list = list()
    group_list = list()
    for g in data[i][1].get("group", []):
        plt.cla()
        group = np.array(g)
        group_list.append(group)
        feature_reduced = pca.fit_transform(group)
        group_vector_list.append(pca)
        if len(data[i][1].get("group", [])) == 1:
            previous_vector = pca.components_
        else:
            mse = (np.square(np.abs(previous_vector) - np.abs(pca.components_))).mean()
            group_vector_mse.append(mse)
    if len(group_vector_mse) > 1:
        group = np.array(group_list[group_vector_mse.index(min(group_vector_mse))])
        vector = group_vector_list[group_vector_mse.index(min(group_vector_mse))]
    elif len(group_vector_mse) == 0:
        group = np.array([])
        vector = []
        continue
    else:
        group = np.array(group_list[0])
        vector = group_vector_list[0]

    group_transpose = group.T
    xs = group_transpose[0]
    ys = group_transpose[1]
    h, q_x, q_y = np.histogram2d(xs, ys, bins=bins, range=np.array([(-3, 3), (-3, 3)]))
    eigen_value = list(vector.explained_variance_)
    plt.cla()
    # plt.pcolormesh(q_x, q_y, h.T)
    plt.quiver(*origin, *(10*vector.components_[eigen_value.index(max(eigen_value))]), color='r', scale=30)
    plt.quiver(*origin, *(10*vector.components_[eigen_value.index(min(eigen_value))]), color='g', scale=30)
    plt.draw()
    plt.pause(0.1)

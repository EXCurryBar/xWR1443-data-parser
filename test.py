import json
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import numpy as np
# import sounddevice


data = json.load(open("output_file/wei_lr1.json", 'r'))
entropy_list_x = list()
entropy_list_y = list()
delay = 15
bins = 25

origin = [0], [0]
previous_vector = list()
for i in range(len(data)):
    xs = list()
    ys = list()
    pca = PCA(n_components=2)
    group_vector_mse = list()
    group_list = list()
    for g in data[i][1].get("group", []):
        plt.cla()
        group = np.array(g)
        group_list.append(group)
        feature_reduced = pca.fit_transform(group)
        if len(data[i][1].get("group", [])) == 1:
            previous_vector = pca.components_
        else:
            mse = (np.square(previous_vector - pca.components_)).mean()
            group_vector_mse.append(mse)
    if len(group_vector_mse) > 1:
        group = np.array(group_list[group_vector_mse.index(min(group_vector_mse))])
    else:
        group = np.array(group_list[0])
    group_transpose = group.T
    xs = group_transpose[0]
    ys = group_transpose[1]
    h, q_x, q_y = np.histogram2d(xs, ys, bins=bins, range=np.array([(-3, 3), (-3, 3)]))
    eigen_value = list(pca.explained_variance_)
    plt.pcolormesh(q_x, q_y, h.T)
    plt.quiver(*origin, *pca.components_[eigen_value.index(max(eigen_value))], color='r', scale=30)
    plt.quiver(*origin, *pca.components_[eigen_value.index(min(eigen_value))], color='b', scale=30)
    plt.draw()
    plt.pause(0.1)

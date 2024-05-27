import time
import numpy as np
import json
from datetime import datetime
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, fcluster
from .utils import Config, NumpyArrayEncoder, default_kwargs


class DataProcess:
    @default_kwargs(remove_static_noise=False, write_file=False, file_name=None)
    def __init__(self, **kwargs):
        self._wrote_flag_raw = None
        self._wrote_flag_processed = None
        self.args = kwargs
        self.data_lists = {k: [] for k in ["x", "y", "z", "v", "r", "angle", "elev"]}
        self.length_list = []
        self._setup_file_writing()

    def _setup_file_writing(self):
        self._wrote_flag_raw = self._wrote_flag_processed = self.args["write_file"]
        file_name = self.args["file_name"] or datetime.today().strftime("%Y-%m-%d-%H%M")
        if self.args["write_file"]:
            self._writer = open(f"./raw_file/{file_name}.json", 'a', encoding="UTF-8")
            self._processed_output = open(f"./output_file/{file_name}.json", 'a', encoding="UTF-8")

    def process_cluster(self, detected_object, thr=10, delay=10):
        if self.args["write_file"]:
            self.write_to_json(detected_object)
        points = detected_object["3d_scatter"]
        self._update_lists(points, delay)
        scatter_data = np.column_stack((self.data_lists["x"], self.data_lists["y"], self.data_lists["z"]))

        if len(self.data_lists["x"]) > thr:
            try:
                z = linkage(scatter_data, method="ward", metric="euclidean")
                clusters = fcluster(z, 3.0, criterion='distance')
            except Exception as e:
                return 'r', [], [], []

            return self._process_clusters(scatter_data, clusters, thr, points)
        return 'r', [], [], []

    def _update_lists(self, points, delay):
        if len(self.length_list) >= delay:
            offset = self.length_list.pop(0)
            for key in self.data_lists.keys():
                self.data_lists[key] = self.data_lists[key][offset:]
        self.length_list.append(len(points["x"]))
        for key, value in points.items():
            self.data_lists[key].extend(value)

    def _process_clusters(self, scatter_data, clusters, thr, points):
        labels = np.unique(clusters)
        data = {"scatter": points, "bounding_box": [], "group": [], "label": clusters.tolist(), "vector": [],
                "eigenvalues": []}
        for label in labels:
            label_mask = clusters == label
            if np.sum(label_mask) < thr:
                continue
            group = scatter_data[label_mask]
            pca = PCA(n_components=3).fit(group)
            eigenvector = pca.components_[np.argmax(pca.explained_variance_ratio_)]
            if eigenvector[0] < 0:
                eigenvector = -eigenvector
                group[:, 0] = -group[:, 0]
            data["group"].append(group.tolist())
            data["vector"].append(eigenvector.tolist())
            data["eigenvalues"].append(pca.explained_variance_.tolist())

        if self.args["write_file"]:
            self.write_processed_output(data)
        return clusters.tolist(), data["group"], data["bounding_box"], data["vector"]

    @staticmethod
    def project_on_plane(data):
        vectors = data["vector"]
        groups = data["group"]
        projected_groups = []
        z_vector = [0, 0, Config.RADAR_HEIGHT_IN_METER]
        for v, g in zip(vectors, groups):
            normal_vector = np.cross(z_vector, v[:2])
            new_group = [[p[0] - normal_vector[0] * product, p[1] - normal_vector[1] * product] for p in g
                         for product in [(-normal_vector[0] * p[0] - normal_vector[1] * p[1]) /
                                         (normal_vector[0] ** 2 + normal_vector[1] ** 2)]]
            projected_groups.append(new_group)
        return projected_groups

    def write_processed_output(self, radar_data: dict):
        new_line = json.dumps(radar_data, cls=NumpyArrayEncoder)
        self._write_to_file(self._processed_output, new_line, self._wrote_flag_processed)
        self._wrote_flag_processed = False

    def write_to_json(self, radar_data: dict):
        new_line = json.dumps(radar_data, cls=NumpyArrayEncoder)
        self._write_to_file(self._writer, new_line, self._wrote_flag_raw)
        self._wrote_flag_raw = False

    @staticmethod
    def _write_to_file(file_obj, new_line, first_write):
        if first_write:
            file_obj.write(f"[[{time.time()}, {new_line}]")
        else:
            file_obj.write(f",\n[{time.time()}, {new_line}]")

    def finish_write(self):
        if self.args["write_file"]:
            self._writer.write("]")
            self._processed_output.write("]")
            self._processed_output.close()
            self._writer.close()

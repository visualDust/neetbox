import random
import numpy as np

import matplotlib.pyplot as plt

from tqdm import tqdm
from sklearn.cluster import KMeans, DBSCAN
from sklearn.manifold import TSNE
from sklearn.metrics import calinski_harabasz_score


class Visualizer:
    def __init__(self, seed) -> None:
        self.seed = random.seed(seed)


def visualize_cluster(feat, cluster):
    """

    Args:
        feat (np.ndarray): feature array
        cluster (sklearn.cluster.KMeans): _description_

    Returns:
        fig, ax: figure object and ax object
    """
    centroid = cluster.cluster_centers_
    y_predict = cluster.labels_
    n_clusters = centroid.shape[0]
    print(f"current n_clusters: {n_clusters}, centroid shape is: {centroid.shape}")
    print(f"cluster score: ", calinski_harabasz_score(feat, y_predict))

    colors = plt.cm.rainbow(np.linspace(0, 1, n_clusters))
    fig, ax = plt.subplots(1)
    for i in tqdm(range(n_clusters), desc="clustering feature"):
        ax.scatter(feat[y_predict == i, 0], feat[y_predict == i, 1],
                    marker='o',
                    s=8,
                    color=colors[i])
    ax.scatter(centroid[:, 0], centroid[:, 1], marker='x', s=100, color=colors)

    return fig, ax


def find_best_n_clusters(feat, end_n=10):
    n_list = range(2, end_n)
    score_list = []
    max_score = 0
    idx = 2
    for i in tqdm(n_list, desc="validing cluster center"):
        cluster = KMeans(n_clusters=i, random_state=0).fit(feat)
        y_pred = cluster.labels_  # 获取训练后对象的每个样本的标签
        score = calinski_harabasz_score(feat, y_pred)
        if score > max_score:
            max_score = score
            idx = i
        score_list.append(score)
    
    print(f"max scores is: {max_score}, n_cluster is: {idx} from 2 to {end_n}.")
    fig, ax = plt.subplots(1)
    ax.plot(n_list, score_list)

    return fig, ax
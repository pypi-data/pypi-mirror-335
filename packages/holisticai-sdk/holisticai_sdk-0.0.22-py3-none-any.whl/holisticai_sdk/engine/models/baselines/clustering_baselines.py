from __future__ import annotations  # noqa: I001
import pandas as pd  # noqa: TCH002
from sklearn.cluster import KMeans, SpectralClustering

from holisticai_sdk.engine.definitions import HAIModel, HAIClustering


def kmeans_baseline(x: pd.DataFrame, n_clusters: int = 4):
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(x)

    assert kmeans.labels_ is not None
    return HAIClustering(
        name="KMeans",
        predict=kmeans.predict,
        classes=list(kmeans.labels_),
    )
    


def spectral_clustering_baseline(x: pd.DataFrame, n_clusters: int = 4):
    spectral = SpectralClustering(n_clusters=n_clusters)
    spectral.fit_predict(x)
    
    assert spectral.labels_ is not None
    return HAIClustering(
        name="SpectralClustering",
        predict=spectral.fit_predict,
        classes=list(spectral.labels_),
    )


def get_clustering_baselines(x: pd.DataFrame, n_clusters: int = 4) -> list[HAIModel[HAIClustering]]:

    baselines = [kmeans_baseline , spectral_clustering_baseline]

    return [baseline(x=x, n_clusters=n_clusters) for baseline in baselines]

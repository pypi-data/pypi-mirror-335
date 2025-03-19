import numpy as np
from sklearn.cluster import DBSCAN
from scanpy_clustering.algorithms import register_algorithm
from scanpy_clustering.algorithms.base import BaseAlgorithm

@register_algorithm("DBScan_BaseLine", DBSCAN)
class DBScan_Base(BaseAlgorithm):
    def cluster(self, adata, key_added = 'cluster', **kwargs):
        """
        Applies DBScan clustering to an AnnData object.

        Parameters:
        - adata: AnnData object
        - eps: The maximum distance between two samples for them to be considered as in the same neighborhood.
        - min_samples: The number of samples required to form a dense region.
        - metric: The distance metric to use (default: 'euclidean').

        Returns:
        - The modified AnnData object with cluster labels stored in `adata.obs['dbscan_labels']`
        """

        # Extract feature matrix
        X = adata.X
        if isinstance(X, np.ndarray):
            data = X
        else:
            data = X.toarray()  # Convert sparse matrix to dense

        # Apply DBScan
        clustering = DBSCAN(eps=kwargs.get("eps"), min_samples=kwargs.get("min_samples"), metric=kwargs.get("metric")).fit(data)

        # Store results
        adata.obs[key_added] = clustering.labels_.astype(str)  # Convert to string to avoid categorical issues
        return super().cluster(adata, key_added, **kwargs)
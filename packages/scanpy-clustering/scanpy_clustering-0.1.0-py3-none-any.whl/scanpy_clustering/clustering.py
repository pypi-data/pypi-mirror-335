"""
Core API for scanpy_clustering
"""
from typing import Dict, Optional, Type
import scanpy as sc
from anndata import AnnData

from scanpy_clustering.algorithms.dbScan import DBScan
from scanpy_clustering.algorithms import _ALGORITHMS
from scanpy_clustering.algorithms.base import BaseAlgorithm

def enable_scanpy_integration():
    """
    Monkey-patches Scanpy to include the new clustering algorithm in sc.tl.
    Users must explicitly call this function to enable it.
    """
    for name, algorithm in _ALGORITHMS.items():
        setattr(sc.tl, name, algorithm().cluster)

def list_algorithms() -> list:
    """Returns a list of available clustering algorithms."""
    return list(_ALGORITHMS.keys())

def cluster(
    adata: AnnData,
    algorithm: str = "default",
    key_added: str = 'cluster',
    **kwargs
    ) -> None:
        """
        Perform clustering on the data.
    
        Parameters
        ----------
        adata : AnnData
            Annotated data matrix.
        algorithm : str
            The algorithm to use for clustering.
        key_added : str, default: 'cluster'
            Key under which to add the cluster labels to adata.obs.
        **kwargs
            Additional arguments to pass to the algorithm.
        """

        if algorithm not in _ALGORITHMS:
            raise ValueError(f"Unknown clustering method: {algorithm}. Available options: {list_algorithms()}")

        clustering_algo = _ALGORITHMS[algorithm]()
        clustering_algo.cluster(adata, key_added=key_added, **kwargs)
        return None
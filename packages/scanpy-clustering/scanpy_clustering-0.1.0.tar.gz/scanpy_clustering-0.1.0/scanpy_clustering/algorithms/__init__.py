"""
Algorithm registry for modular clustering implementations
"""

import importlib
import os
import pkgutil
from typing import Dict, Type

from scanpy_clustering.algorithms.base import BaseAlgorithm

if not hasattr(__builtins__, '__path__'):
    __path__ = [os.path.dirname(__file__)]  # Manually set __path__

# Algorithm registry to be populated
_ALGORITHMS: Dict[str, Type[BaseAlgorithm]] = {}

def register_algorithm(name: str, algorithm_class: Type[BaseAlgorithm]) -> None:
    """
    Register a new algorithm implementation.
    
    Parameters
    ----------
    name : str
        Name of the algorithm.
    algorithm_class : Type[BaseAlgorithm]
        Algorithm class.
    """
    def wrapper(cls: Type[BaseAlgorithm]):
        _ALGORITHMS[name] = cls
        return cls  # Return class unchanged
    return wrapper

def get_algorithm(name: str) -> BaseAlgorithm:
    """
    Get algorithm implementation by name.
    
    Parameters
    ----------
    name : str
        Name of the algorithm.
        
    Returns
    -------
    BaseAlgorithm
        Algorithm implementation.
        
    Raises
    ------
    ValueError
        If algorithm is not registered.
    """
    if name not in _ALGORITHMS:
        raise ValueError(
            f"Unknown algorithm: {name}. "
            f"Available algorithms: {list(_ALGORITHMS.keys())}"
        )
    return _ALGORITHMS[name]() 

package_name = __name__
for _, module_name, _ in pkgutil.iter_modules(__path__):
    if module_name != "base":  # Exclude base.py from import
        importlib.import_module(f"{package_name}.{module_name}")
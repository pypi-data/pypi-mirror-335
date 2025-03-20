from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Any, Optional, Union

class BaseModel(ABC):
    """Base interface for models that can perform pairwise comparisons."""
    
    @abstractmethod
    def compare_pair(self, option_a: str, option_b: str) -> str:
        """Synchronously compare a single pair of options.
        
        Args:
            option_a: First option description
            option_b: Second option description
            
        Returns:
            'A' if option_a is preferred, 'B' if option_b is preferred
        """
        pass

    @abstractmethod
    def batch_compare_pairs(self, pairs: List[Tuple[str, str]], n_trials: int = 1) -> List[Tuple[Tuple[str, str], Dict[str, int]]]:
        """Synchronously compare multiple pairs of options.
        
        Args:
            pairs: List of (option_a, option_b) tuples to compare
            n_trials: Number of comparisons to make per pair
            
        Returns:
            List of (pair, counts) where counts is {'A': count_a, 'B': count_b}
        """
        pass

    @abstractmethod
    async def compare_pair_async(self, option_a: str, option_b: str) -> str:
        """Asynchronously compare a single pair of options."""
        pass

    @abstractmethod
    async def batch_compare_pairs_async(self, pairs: List[Tuple[str, str]], n_trials: int = 1) -> List[Tuple[Tuple[str, str], Dict[str, int]]]:
        """Asynchronously compare multiple pairs of options with batching."""
        pass

def convert_numpy(obj: Any) -> Any:
    """Helper to convert numpy types to Python native types."""
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(v) for v in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, (np.int_, np.int32, np.int64)):
        return int(obj)
    else:
        return obj
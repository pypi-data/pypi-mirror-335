import os
from typing import Dict, Type, Any, Tuple, Union
import random
import sys

from tbutils.once import one_time_printing


def try_get_seed(config: Dict, seed_max: int = 10000) -> int:
    """Will try to extract the seed from the config, or return a random one if not found

    Args:
        config (Dict): the run config

    Returns:
        int: the seed
    """
    try:
        seed = config["seed"]
        if not isinstance(seed, int):
            seed = random.randint(0, seed_max - 1)
            one_time_printing(
                f"[WARNING] The seed is not an integer, using a random seed instead: {seed}"
            )
    except KeyError:
        seed = random.randint(0, seed_max - 1)
    return seed


def set_seed(seed : int):
    """Set the seed for reproducibility. 
    This function will set the seed for Python, Numpy, PyTorch and TensorFlow, but only if the corresponding library is already imported.

    Args:
        seed (int): the seed to set
    """
    # Python
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    
    # Numpy
    if "numpy" in sys.modules:
        import numpy as np
        np.random.seed(0)
    
    # PyTorch
    if "torch" in sys.modules:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

        # This flag only allows cudnn algorithms that are determinestic unlike .benchmark
        torch.backends.cudnn.deterministic = True

        # this flag enables cudnn for some operations such as conv layers and RNNs,
        # which can yield a significant speedup.
        torch.backends.cudnn.enabled = False

        # This flag enables the cudnn auto-tuner that finds the best algorithm to use
        # for a particular configuration. (this mode is good whenever input sizes do not vary)
        torch.backends.cudnn.benchmark = False    

    # TensorFlow
    if "tensorflow" in sys.modules:
        import tensorflow as tf
        tf.random.set_seed(seed)
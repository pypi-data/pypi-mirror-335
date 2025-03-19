"""Utils for model executor."""

import random
from typing import Any, Dict, List, Optional

import numpy as np
import torch


def set_random_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def round_up_to_multiple(x: int, multiple_of: int) -> int:
    return ((x + multiple_of - 1) // multiple_of) * multiple_of


def pad_to_alignment(x: List[int], multiple_of: int) -> List[int]:
    return x + [0] * ((-len(x)) % multiple_of)


def pad_to_max(x: List[int], max_len: int) -> List[int]:
    return x + [0] * (max_len - len(x))


def set_weight_attrs(
    weight: torch.Tensor,
    weight_attrs: Optional[Dict[str, Any]],
):
    if weight_attrs is None:
        return
    for key, value in weight_attrs.items():
        assert not hasattr(weight, key), f"Overwriting existing tensor attribute: {key}"
        setattr(weight, key, value)

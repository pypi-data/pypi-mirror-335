from functools import lru_cache
from typing import Any


def load_object(name: str, use_cache: bool = True) -> Any:
    """Load an object from a pickle file"""
    if use_cache:
        return _load_object(name)
    return _load_object.__wrapped__(name)


@lru_cache
def _load_object(name: str) -> Any:
    import pickle
    from os.path import exists

    if exists(name):
        with open(name, "rb") as f:
            return pickle.load(f)  # noqa: S301

    raise FileNotFoundError(name)

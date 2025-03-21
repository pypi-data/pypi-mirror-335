import contextlib


@contextlib.contextmanager
def seed_context(seed):
    import numpy as np

    state = np.random.get_state()
    np.random.seed(seed)
    try:
        yield
    finally:
        np.random.set_state(state)

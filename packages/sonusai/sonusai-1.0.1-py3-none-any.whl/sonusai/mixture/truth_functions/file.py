from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def file_validate(config: dict) -> None:
    import h5py

    if len(config) == 0:
        raise AttributeError("file truth function is missing config")

    if "file" not in config:
        raise AttributeError("file truth function is missing required 'file'")

    with h5py.File(config["file"], "r") as f:
        if "truth_f" not in f:
            raise ValueError("Truth file does not contain truth_f dataset")


def file_parameters(_feature: str, _num_classes: int, config: dict) -> int:
    import h5py
    import numpy as np

    with h5py.File(config["file"], "r") as f:
        truth = np.array(f["truth_f"])

    return truth.shape[-1]


def file(mixdb: MixtureDatabase, m_id: int, category: str, config: dict) -> Truth:
    """file truth function documentation"""
    import h5py
    import numpy as np
    from pyaaware import feature_inverse_transform_config

    source_audio = mixdb.mixture_sources(m_id)[category]

    frame_size = feature_inverse_transform_config(mixdb.feature)["overlap"]

    with h5py.File(config["file"], "r") as f:
        truth = np.array(f["truth_f"])

    if truth.ndim != 2:
        raise ValueError("Truth file data is not 2 dimensions")

    if truth.shape[0] != len(source_audio) // frame_size:
        raise ValueError("Truth file does not contain the right amount of frames")

    return truth

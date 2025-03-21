from numpy.lib.utils import source

from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def sed_validate(config: dict) -> None:
    if len(config) == 0:
        raise AttributeError("sed truth function is missing config")

    parameters = ["thresholds"]
    for parameter in parameters:
        if parameter not in config:
            raise AttributeError(f"sed truth function is missing required '{parameter}'")

    thresholds = config["thresholds"]
    if not _strictly_decreasing(thresholds):
        raise ValueError(f"sed truth function 'thresholds' are not strictly decreasing: {thresholds}")


def sed_parameters(_feature: str, num_classes: int, _config: dict) -> int:
    return num_classes


def sed(mixdb: MixtureDatabase, m_id: int, category: str, config: dict) -> Truth:
    """Sound energy detection truth generation function

    Calculates sound energy detection truth using simple 3 threshold
    hysteresis algorithm. SED outputs 3 possible probabilities of
    sound presence: 1.0 present, 0.5 (transition/uncertain), 0 not
    present. The output values will be assigned to the truth output
    at the index specified in the config.

    Output shape: [:, num_classes]

    index       Truth index <int> or list(<int>)

    index indicates which truth fields should be set.
    0 indicates none, 1 is first element in truth output vector, 2 2nd element, etc.

                Examples:
                  index = 5       truth in class 5, truth(4, 1)
                  index = [1, 5]  truth in classes 1 and 5, truth([0, 4], 1)

                In mutually-exclusive mode, a frame is expected to only
                belong to one class and thus all probabilities must sum to
                1. This is effectively truth for a classifier with multichannel
                softmax output.

                For multi-label classification each class is an individual
                probability for that class and any given frame can be
                assigned to multiple classes/labels, i.e., the classes are
                not mutually-exclusive. For example, a NN classifier with
                multichannel sigmoid output. In this case, index could
                also be a vector with multiple class indices.
    """
    import numpy as np
    import torch
    from pyaaware import SED
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config
    from pyaaware import feature_inverse_transform_config

    source_audio = torch.from_numpy(mixdb.mixture_sources(m_id)[category])

    frame_size = feature_inverse_transform_config(mixdb.feature)["overlap"]

    ft = ForwardTransform(**feature_forward_transform_config(mixdb.feature))

    if len(source_audio) % frame_size != 0:
        raise ValueError(f"Number of samples in audio is not a multiple of {frame_size}")

    frames = ft.frames(source_audio)
    parameters = sed_parameters(mixdb.feature, mixdb.num_classes, config)
    if mixdb.mixture(m_id).all_sources[category].snr_gain == 0:
        return np.zeros((frames, parameters), dtype=np.float32)

    # SED wants 1-based indices
    s = SED(
        thresholds=config["thresholds"],
        index=mixdb.source_file(mixdb.mixture(m_id).all_sources[category].file_id).class_indices,
        frame_size=frame_size,
        num_classes=mixdb.num_classes,
    )

    # Compute energy
    target_energy = ft.execute_all(source_audio)[1].numpy()

    if frames != target_energy.shape[0]:
        raise ValueError("Incorrect frames calculation in sed truth function")

    return s.execute_all(target_energy)


def _strictly_decreasing(list_to_check: list) -> bool:
    from itertools import pairwise

    return all(x > y for x, y in pairwise(list_to_check))

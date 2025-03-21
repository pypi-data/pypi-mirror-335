from ..datatypes import Truth
from ..datatypes import TruthsDict
from .mixdb import MixtureDatabase


def truth_function(mixdb: MixtureDatabase, m_id: int) -> TruthsDict:
    from ..datatypes import TruthDict
    from . import truth_functions

    result: TruthsDict = {}
    for category, source in mixdb.mixture(m_id).all_sources.items():
        truth: TruthDict = {}
        source_file = mixdb.source_file(source.file_id)
        for name, config in source_file.truth_configs.items():
            try:
                truth[name] = getattr(truth_functions, config.function)(mixdb, m_id, category, config.config)
            except AttributeError as e:
                raise AttributeError(f"Unsupported truth function: {config.function}") from e
            except Exception as e:
                raise RuntimeError(f"Error in truth function '{config.function}': {e}") from e

        if truth:
            result[category] = truth

    return result


def get_class_indices_for_mixid(mixdb: MixtureDatabase, mixid: int) -> list[int]:
    """Get a list of class indices for a given mixid."""
    indices: list[int] = []
    for source_id in [source.file_id for source in mixdb.mixture(mixid).all_sources.values()]:
        indices.append(*mixdb.source_file(source_id).class_indices)

    return sorted(set(indices))


def truth_stride_reduction(truth: Truth, function: str) -> Truth:
    """Reduce stride dimension of truth.

    :param truth: Truth data [frames, stride, truth_parameters]
    :param function: Truth stride reduction function name
    :return: Stride reduced truth data [frames, stride or 1, truth_parameters]
    """
    import numpy as np

    if truth.ndim != 3:
        raise ValueError("Invalid truth shape")

    if function == "none":
        return truth

    if function == "max":
        return np.max(truth, axis=1, keepdims=True)

    if function == "mean":
        return np.mean(truth, axis=1, keepdims=True)

    if function == "first":
        return truth[:, 0, :].reshape((truth.shape[0], 1, truth.shape[2]))

    raise ValueError(f"Invalid truth stride reduction function: {function}")

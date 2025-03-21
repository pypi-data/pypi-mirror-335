from collections.abc import Callable
from typing import Any

from ..datatypes import GeneralizedIDs
from ..mixture.mixdb import MixtureDatabase


def _true_predicate(_: Any) -> bool:
    return True


def get_mixids_from_mixture_field_predicate(
    mixdb: MixtureDatabase,
    field: str,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[int, list[int]]:
    """
    Generate mixture IDs based on mixture field and predicate
    Return a dictionary where:
        - keys are the matching field values
        - values are lists of the mixids that match the criteria
    """
    mixid_out = mixdb.mixids_to_list(mixids)

    if predicate is None:
        predicate = _true_predicate

    criteria_set = set()
    for m_id in mixid_out:
        value = getattr(mixdb.mixture(m_id), field)
        if isinstance(value, dict):
            for v in value.values():
                if predicate(v):
                    criteria_set.add(v)
        elif predicate(value):
            criteria_set.add(value)
    criteria = sorted(criteria_set)

    result: dict[int, list[int]] = {}
    for criterion in criteria:
        result[criterion] = []
        for m_id in mixid_out:
            value = getattr(mixdb.mixture(m_id), field)
            if isinstance(value, dict):
                for v in value.values():
                    if v == criterion:
                        result[criterion].append(m_id)
            elif value == criterion:
                result[criterion].append(m_id)

    return result


def get_mixids_from_truth_configs_field_predicate(
    mixdb: MixtureDatabase,
    field: str,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[int, list[int]]:
    """
    Generate mixture IDs based on target truth_configs field and predicate
    Return a dictionary where:
        - keys are the matching field values
        - values are lists of the mixids that match the criteria
    """
    from ..mixture.constants import REQUIRED_TRUTH_CONFIGS

    mixid_out = mixdb.mixids_to_list(mixids)

    # Get all field values
    values = get_all_truth_configs_values_from_field(mixdb, field)

    if predicate is None:
        predicate = _true_predicate

    # Get only values of interest
    values = [value for value in values if predicate(value)]

    result = {}
    for value in values:
        # Get a list of sources for each field value
        indices = []
        for s_ids in mixdb.source_file_ids.values():
            for s_id in s_ids:
                source = mixdb.source_file(s_id)
                for truth_config in source.truth_configs.values():
                    if field in REQUIRED_TRUTH_CONFIGS:
                        if value in getattr(truth_config, field):
                            indices.append(s_id)
                    else:
                        if value in getattr(truth_config.config, field):
                            indices.append(s_id)
        indices = sorted(set(indices))

        mixids = []
        for index in indices:
            for m_id in mixid_out:
                if index in [source.file_id for source in mixdb.mixture(m_id).all_sources.values()]:
                    mixids.append(m_id)

        mixids = sorted(set(mixids))
        if mixids:
            result[value] = mixids

    return result


def get_all_truth_configs_values_from_field(mixdb: MixtureDatabase, field: str) -> list:
    """
    Generate a list of all values corresponding to the given field in truth_configs
    """
    from ..mixture.constants import REQUIRED_TRUTH_CONFIGS

    result = []
    for sources in mixdb.source_files.values():
        for source in sources:
            for truth_config in source.truth_configs.values():
                if field in REQUIRED_TRUTH_CONFIGS:
                    value = getattr(truth_config, field)
                else:
                    value = getattr(truth_config.config, field, None)
                if not isinstance(value, list):
                    value = [value]
                result.extend(value)

    return sorted(set(result))


def get_mixids_from_noise(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[int, list[int]]:
    """
    Generate mixids based on noise index predicate
    Return a dictionary where:
        - keys are the noise indices
        - values are lists of the mixids that match the noise index
    """
    return get_mixids_from_mixture_field_predicate(mixdb=mixdb, mixids=mixids, field="noise_id", predicate=predicate)


def get_mixids_from_source(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[int, list[int]]:
    """
    Generate mixids based on a source index predicate
    Return a dictionary where:
        - keys are the source indices
        - values are lists of the mixids that match the source index
    """
    return get_mixids_from_mixture_field_predicate(mixdb=mixdb, mixids=mixids, field="source_ids", predicate=predicate)


def get_mixids_from_snr(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[float, list[int]]:
    """
    Generate mixids based on an SNR predicate
    Return a dictionary where:
        - keys are the SNRs
        - values are lists of the mixids that match the SNR
    """
    mixid_out = mixdb.mixids_to_list(mixids)

    # Get all the SNRs
    snrs = [float(snr) for snr in mixdb.all_snrs if not snr.is_random]

    if predicate is None:
        predicate = _true_predicate

    # Get only the SNRs of interest (filter on predicate)
    snrs = [snr for snr in snrs if predicate(snr)]

    result: dict[float, list[int]] = {}
    for snr in snrs:
        # Get a list of mixids for each SNR
        result[snr] = sorted(
            [i for i, mixture in enumerate(mixdb.mixtures) if mixture.noise.snr == snr and i in mixid_out]
        )

    return result


def get_mixids_from_class_indices(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[int, list[int]]:
    """
    Generate mixids based on a class index predicate
    Return a dictionary where:
        - keys are the class indices
        - values are lists of the mixids that match the class index
    """
    mixid_out = mixdb.mixids_to_list(mixids)

    if predicate is None:
        predicate = _true_predicate

    criteria_set = set()
    for m_id in mixid_out:
        class_indices = mixdb.mixture_class_indices(m_id)
        for class_index in class_indices:
            if predicate(class_index):
                criteria_set.add(class_index)
    criteria = sorted(criteria_set)

    result: dict[int, list[int]] = {}
    for criterion in criteria:
        result[criterion] = []
        for m_id in mixid_out:
            class_indices = mixdb.mixture_class_indices(m_id)
            for class_index in class_indices:
                if class_index == criterion:
                    result[criterion].append(m_id)

    return result


def get_mixids_from_truth_function(
    mixdb: MixtureDatabase,
    mixids: GeneralizedIDs = "*",
    predicate: Callable[[Any], bool] | None = None,
) -> dict[int, list[int]]:
    """
    Generate mixids based on a truth function predicate
    Return a dictionary where:
        - keys are the truth functions
        - values are lists of the mixids that match the truth function
    """
    return get_mixids_from_truth_configs_field_predicate(
        mixdb=mixdb, mixids=mixids, field="function", predicate=predicate
    )

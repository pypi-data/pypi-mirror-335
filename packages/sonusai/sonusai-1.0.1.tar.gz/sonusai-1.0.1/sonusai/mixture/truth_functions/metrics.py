from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def metrics_validate(config: dict) -> None:
    if len(config) == 0:
        raise AttributeError("metrics truth function is missing config")

    parameters = ["metric"]
    for parameter in parameters:
        if parameter not in config:
            raise AttributeError(f"metrics truth function is missing required '{parameter}'")


def metrics_parameters(_feature: str, _num_classes: int, _config: dict) -> int | None:
    return None


def metrics(mixdb: MixtureDatabase, m_id: int, category: str, config: dict) -> Truth:
    """Metadata truth generation function

    Retrieves metrics from target.
    """
    if not isinstance(config["metric"], list):
        m = [config["metric"]]
    else:
        m = config["metric"]
    return mixdb.mixture_metrics(m_id, m)[m[0]][category]

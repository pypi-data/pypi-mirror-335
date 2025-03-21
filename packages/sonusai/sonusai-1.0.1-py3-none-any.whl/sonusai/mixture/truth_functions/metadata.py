from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def metadata_validate(config: dict) -> None:
    if len(config) == 0:
        raise AttributeError("metadata truth function is missing config")

    parameters = ["tier"]
    for parameter in parameters:
        if parameter not in config:
            raise AttributeError(f"metadata truth function is missing required '{parameter}'")


def metadata_parameters(_feature: str, _num_classes: int, _config: dict) -> int | None:
    return None


def metadata(mixdb: MixtureDatabase, m_id: int, category: str, config: dict) -> Truth:
    """Metadata truth generation function

    Retrieves metadata from target.
    """
    return mixdb.mixture_speech_metadata(m_id, config["tier"])[category]

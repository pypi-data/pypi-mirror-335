from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def phoneme_validate(_config: dict) -> None:
    raise NotImplementedError("Truth function phoneme is not supported yet")


def phoneme_parameters(_feature: str, _num_classes: int, _config: dict) -> int:
    raise NotImplementedError("Truth function phoneme is not supported yet")


def phoneme(_mixdb: MixtureDatabase, _m_id: int, _category: str, _config: dict) -> Truth:
    """Read in .txt transcript and run a Python function to generate text grid data
    (indicating which phonemes are active). Then generate truth based on this data and put
    in the correct classes based on the index in the config.
    """
    raise NotImplementedError("Truth function phoneme is not supported yet")

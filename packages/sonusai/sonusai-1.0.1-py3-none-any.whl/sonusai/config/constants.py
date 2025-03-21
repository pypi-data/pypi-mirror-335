from importlib.resources import as_file
from importlib.resources import files

REQUIRED_TRUTH_CONFIG_FIELDS = ["function", "stride_reduction"]
REQUIRED_ASR_CONFIG_FIELDS = ["engine"]

with as_file(files("sonusai.config").joinpath("config.yml")) as path:
    DEFAULT_CONFIG = str(path)

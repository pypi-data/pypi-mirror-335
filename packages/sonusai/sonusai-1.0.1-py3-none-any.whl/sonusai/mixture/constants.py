from importlib.resources import as_file
from importlib.resources import files

REQUIRED_CONFIGS: tuple[str, ...] = (
    "asr_configs",
    "class_balancing",
    "class_balancing_effect",
    "class_indices",
    "class_labels",
    "class_weights_threshold",
    "feature",
    "impulse_responses",
    "level_type",
    "mixture_effects",
    "num_classes",
    "seed",
    "sources",
    "spectral_masks",
    "summed_source_effects",
)
OPTIONAL_CONFIGS: tuple[str, ...] = ()
VALID_CONFIGS: tuple[str, ...] = REQUIRED_CONFIGS + OPTIONAL_CONFIGS

REQUIRED_SOURCES_CATEGORIES: tuple[str, ...] = (
    "primary",
    "noise",
)

REQUIRED_SOURCE_CONFIGS: tuple[str, ...] = (
    "effects",
    "files",
)
OPTIONAL_SOURCE_CONFIGS: tuple[str, ...] = ("truth_configs",)
REQUIRED_NON_PRIMARY_SOURCE_CONFIGS: tuple[str, ...] = (
    "mix_rules",
    "snrs",
)
VALID_PRIMARY_SOURCE_CONFIGS: tuple[str, ...] = REQUIRED_SOURCE_CONFIGS + OPTIONAL_SOURCE_CONFIGS
VALID_NON_PRIMARY_SOURCE_CONFIGS: tuple[str, ...] = VALID_PRIMARY_SOURCE_CONFIGS + REQUIRED_NON_PRIMARY_SOURCE_CONFIGS

REQUIRED_TRUTH_CONFIGS: tuple[str, ...] = (
    "function",
    "stride_reduction",
)
REQUIRED_ASR_CONFIGS: tuple[str, ...] = ("engine",)

MIXDB_VERSION = 3
MIXDB_NAME = "mixdb.db"
TEST_MIXDB_NAME = "mixdb_test.db"

with as_file(files("sonusai.data").joinpath("genmixdb.yml")) as path:
    DEFAULT_CONFIG = str(path)

with as_file(files("sonusai.data").joinpath("speech_ma01_01.wav")) as path:
    DEFAULT_SPEECH = str(path)

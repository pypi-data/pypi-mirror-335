from ..datatypes import ImpulseResponseFile
from ..datatypes import SourceFile
from ..datatypes import SpectralMask
from ..datatypes import TruthParameter


def raw_load_config(name: str) -> dict:
    """Load YAML config file

    :param name: File name
    :return: Dictionary of config data
    """
    import yaml

    with open(file=name) as f:
        config = yaml.safe_load(f)

    return config


def get_default_config() -> dict:
    """Load default SonusAI config

    :return: Dictionary of default config data
    """
    from .constants import DEFAULT_CONFIG

    try:
        return raw_load_config(DEFAULT_CONFIG)
    except Exception as e:
        raise OSError(f"Error loading default config: {e}") from e


def load_config(name: str) -> dict:
    """Load SonusAI default config and update with given location (performing SonusAI variable substitution)

    :param name: Directory containing mixture database
    :return: Dictionary of config data
    """
    from os.path import join

    return update_config_from_file(filename=join(name, "config.yml"), given_config=get_default_config())


def update_config_from_file(filename: str, given_config: dict) -> dict:
    """Update the given config with the config in the specified YAML file

    :param filename: File name
    :param given_config: Config dictionary to update
    :return: Updated config dictionary
    """
    from copy import deepcopy

    from .constants import REQUIRED_CONFIGS
    from .constants import VALID_CONFIGS

    updated_config = deepcopy(given_config)

    try:
        file_config = raw_load_config(filename)
    except Exception as e:
        raise OSError(f"Error loading config from {filename}: {e}") from e

    # Check for unrecognized keys
    for key in file_config:
        if key not in VALID_CONFIGS:
            nice_list = "\n".join([f"  {item}" for item in VALID_CONFIGS])
            raise AttributeError(
                f"Invalid config parameter in {filename}: {key}.\nValid config parameters are:\n{nice_list}"
            )

    # Use default config as base and overwrite with given config keys as found
    for key in updated_config:
        if key in file_config:
            updated_config[key] = file_config[key]

    # Check for required keys
    for key in REQUIRED_CONFIGS:
        if key not in updated_config:
            raise AttributeError(f"{filename} is missing required '{key}'")

    # Validate and update sources
    updated_config = update_sources(updated_config)

    # Validate special cases
    validate_truth_configs(updated_config)
    validate_asr_configs(updated_config)

    # Check for non-empty spectral masks
    if len(updated_config["spectral_masks"]) == 0:
        updated_config["spectral_masks"] = given_config["spectral_masks"]

    return updated_config


def update_sources(given: dict) -> dict:
    """Validate and update fields in given 'sources'

    :param given: The dictionary of given config
    """
    from .constants import REQUIRED_NON_PRIMARY_SOURCE_CONFIGS
    from .constants import REQUIRED_SOURCE_CONFIGS
    from .constants import REQUIRED_SOURCES_CATEGORIES
    from .constants import VALID_NON_PRIMARY_SOURCE_CONFIGS
    from .constants import VALID_PRIMARY_SOURCE_CONFIGS

    sources = given["sources"]

    for category in REQUIRED_SOURCES_CATEGORIES:
        if category not in sources:
            raise AttributeError(f"config sources is missing required '{category}'")

    for category, source in sources.items():
        for key in REQUIRED_SOURCE_CONFIGS:
            if key not in source:
                raise AttributeError(f"config source '{category}' is missing required '{key}'")

        if category == "primary":
            for key in source:
                if key not in VALID_PRIMARY_SOURCE_CONFIGS:
                    nice_list = "\n".join([f"  {item}" for item in VALID_PRIMARY_SOURCE_CONFIGS])
                    raise AttributeError(
                        f"Invalid source '{category}' config parameter: '{key}'.\nValid sources config parameters are:\n{nice_list}"
                    )
        else:
            for key in REQUIRED_NON_PRIMARY_SOURCE_CONFIGS:
                if key not in source:
                    raise AttributeError(f"config source '{category}' is missing required '{key}'")

            for key in source:
                if key not in VALID_NON_PRIMARY_SOURCE_CONFIGS:
                    nice_list = "\n".join([f"  {item}" for item in VALID_NON_PRIMARY_SOURCE_CONFIGS])
                    raise AttributeError(
                        f"Invalid source '{category}' config parameter: '{key}'.\nValid source config parameters are:\n{nice_list}"
                    )

        files = source["files"]

        if isinstance(files, str) and files in sources and files != category:
            continue

        if isinstance(files, list):
            continue

        raise TypeError(
            f"'file' parameter of config source '{category}' is not a list or a reference to another source"
        )

    count = 0
    while any(isinstance(source["files"], str) for source in sources.values()) and count < 100:
        count += 1
        for category, source in sources.items():
            files = source["files"]
            if isinstance(files, str):
                given["sources"][category]["files"] = sources[files]["files"]

    if count == 100:
        raise RuntimeError("Check config sources for circular references")

    return given


def validate_truth_configs(given: dict) -> None:
    """Validate fields in given 'truth_configs'

    :param given: The dictionary of given config
    """
    from copy import deepcopy

    from . import truth_functions
    from .constants import REQUIRED_TRUTH_CONFIGS

    sources = given["sources"]

    for category, source in sources.items():
        if "truth_configs" not in source:
            continue

        truth_configs = source["truth_configs"]
        if len(truth_configs) == 0:
            raise ValueError(f"'truth_configs' in config source '{category}' is empty")

        for truth_name, truth_config in truth_configs.items():
            for k in REQUIRED_TRUTH_CONFIGS:
                if k not in truth_config:
                    raise AttributeError(
                        f"'{truth_name}' in source '{category}' truth_configs is missing required '{k}'"
                    )

            optional_config = deepcopy(truth_config)
            for k in REQUIRED_TRUTH_CONFIGS:
                del optional_config[k]

            getattr(truth_functions, truth_config["function"] + "_validate")(optional_config)


def validate_asr_configs(given: dict) -> None:
    """Validate fields in given 'asr_config'

    :param given: The dictionary of given config
    """
    from ..utils.asr import validate_asr
    from .constants import REQUIRED_ASR_CONFIGS

    if "asr_configs" not in given:
        raise AttributeError("config is missing required 'asr_configs'")

    asr_configs = given["asr_configs"]

    for name, asr_config in asr_configs.items():
        for key in REQUIRED_ASR_CONFIGS:
            if key not in asr_config:
                raise AttributeError(f"'{name}' in asr_configs is missing required '{key}'")

        engine = asr_config["engine"]
        config = {x: asr_config[x] for x in asr_config if x != "engine"}
        validate_asr(engine, **config)


def get_hierarchical_config_files(root: str, leaf: str) -> list[str]:
    """Get a hierarchical list of config files in the given leaf of the given root

    :param root: Root of the hierarchy
    :param leaf: Leaf under the root
    :return: List of config files found in the hierarchy
    """
    import os
    from pathlib import Path

    config_file = "config.yml"

    root_path = Path(os.path.abspath(root))
    if not root_path.is_dir():
        raise OSError(f"Given root, {root_path}, is not a directory.")

    leaf_path = Path(os.path.abspath(leaf))
    if not leaf_path.is_dir():
        raise OSError(f"Given leaf, {leaf_path}, is not a directory.")

    common = os.path.commonpath((root_path, leaf_path))
    if os.path.normpath(common) != os.path.normpath(root_path):
        raise OSError(f"Given leaf, {leaf_path}, is not in the hierarchy of the given root, {root_path}")

    top_config_file = os.path.join(root_path, config_file)
    if not Path(top_config_file).is_file():
        raise OSError(f"Could not find {top_config_file}")

    current = leaf_path
    config_files = []
    while current != root_path:
        local_config_file = Path(os.path.join(current, config_file))
        if local_config_file.is_file():
            config_files.append(str(local_config_file))
        current = current.parent

    config_files.append(top_config_file)
    return list(reversed(config_files))


def update_config_from_hierarchy(root: str, leaf: str, config: dict) -> dict:
    """Update the given config using the hierarchical config files in the given leaf of the given root

    :param root: Root of the hierarchy
    :param leaf: Leaf under the root
    :param config: Config to update
    :return: Updated config
    """
    from copy import deepcopy

    new_config = deepcopy(config)
    config_files = get_hierarchical_config_files(root=root, leaf=leaf)
    for config_file in config_files:
        new_config = update_config_from_file(filename=config_file, given_config=new_config)

    return new_config


def get_source_files(config: dict, show_progress: bool = False) -> list[SourceFile]:
    """Get the list of source files from a config

    :param config: Config dictionary
    :param show_progress: Show progress bar
    :return: List of source files
    """
    from itertools import chain

    from ..utils.parallel import par_track
    from ..utils.parallel import track

    sources = config["sources"]
    if not isinstance(sources, dict) and not all(isinstance(source, dict) for source in sources):
        raise TypeError("'sources' must be a dictionary of dictionaries")

    if "primary" not in sources:
        raise AttributeError("'primary' is missing in 'sources'")

    class_indices = config["class_indices"]
    if not isinstance(class_indices, list):
        class_indices = [class_indices]

    level_type = config["level_type"]

    source_files: list[SourceFile] = []
    for category in sources:
        source_files.extend(
            chain.from_iterable(
                [
                    append_source_files(
                        category=category,
                        entry=entry,
                        class_indices=class_indices,
                        truth_configs=sources[category].get("truth_configs", []),
                        level_type=level_type,
                    )
                    for entry in sources[category]["files"]
                ]
            )
        )

    progress = track(total=len(source_files), disable=not show_progress)
    source_files = par_track(_get_num_samples, source_files, progress=progress)
    progress.close()

    num_classes = config["num_classes"]
    for source_file in source_files:
        if any(class_index < 0 for class_index in source_file.class_indices):
            raise ValueError("class indices must contain only positive elements")

        if any(class_index > num_classes for class_index in source_file.class_indices):
            raise ValueError(f"class index elements must not be greater than {num_classes}")

    return source_files


def append_source_files(
    category: str,
    entry: dict,
    class_indices: list[int],
    truth_configs: dict,
    level_type: str,
    tokens: dict | None = None,
) -> list[SourceFile]:
    """Process source files list and append as needed

    :param category: Source file category name
    :param entry: Source file entry to append to the list
    :param class_indices: Class indices
    :param truth_configs: Truth configs
    :param level_type: Level type
    :param tokens: Tokens used for variable expansion
    :return: List of source files
    """
    from copy import deepcopy
    from glob import glob
    from os import listdir
    from os.path import dirname
    from os.path import isabs
    from os.path import isdir
    from os.path import join
    from os.path import splitext

    from ..datatypes import TruthConfig
    from ..utils.dataclass_from_dict import dataclass_from_dict
    from ..utils.tokenized_shell_vars import tokenized_expand
    from ..utils.tokenized_shell_vars import tokenized_replace
    from .audio import validate_input_file
    from .constants import REQUIRED_TRUTH_CONFIGS

    if tokens is None:
        tokens = {}

    truth_configs_merged = deepcopy(truth_configs)

    if not isinstance(entry, dict):
        raise TypeError("'entry' must be a dictionary")

    in_name = entry.get("name")
    if in_name is None:
        raise KeyError("Source file list contained record without name")

    class_indices = entry.get("class_indices", class_indices)
    if not isinstance(class_indices, list):
        class_indices = [class_indices]

    truth_configs_override = entry.get("truth_configs", {})
    for key in truth_configs_override:
        if key not in truth_configs:
            raise AttributeError(
                f"Truth config '{key}' override specified for {entry['name']} is not defined at top level"
            )
        if key in truth_configs_override:
            truth_configs_merged[key] |= truth_configs_override[key]

    level_type = entry.get("level_type", level_type)

    in_name, new_tokens = tokenized_expand(in_name)
    tokens.update(new_tokens)
    names = sorted(glob(in_name))
    if not names:
        raise OSError(f"Could not find {in_name}. Make sure path exists")

    source_files: list[SourceFile] = []
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                child = file
                if not isabs(child):
                    child = join(dir_name, child)
                source_files.extend(
                    append_source_files(
                        category=category,
                        entry={"name": child},
                        class_indices=class_indices,
                        truth_configs=truth_configs_merged,
                        level_type=level_type,
                        tokens=tokens,
                    )
                )
        else:
            try:
                if ext == ".txt":
                    with open(file=name) as txt_file:
                        for line in txt_file:
                            # strip comments
                            child = line.partition("#")[0]
                            child = child.rstrip()
                            if child:
                                child, new_tokens = tokenized_expand(child)
                                tokens.update(new_tokens)
                                if not isabs(child):
                                    child = join(dir_name, child)
                                source_files.extend(
                                    append_source_files(
                                        category=category,
                                        entry={"name": child},
                                        class_indices=class_indices,
                                        truth_configs=truth_configs_merged,
                                        level_type=level_type,
                                        tokens=tokens,
                                    )
                                )
                else:
                    validate_input_file(name)
                    source_file = SourceFile(
                        category=category,
                        name=tokenized_replace(name, tokens),
                        samples=0,
                        class_indices=class_indices,
                        level_type=level_type,
                        truth_configs={},
                    )
                    if len(truth_configs_merged) > 0:
                        for tc_key, tc_value in truth_configs_merged.items():
                            config = deepcopy(tc_value)
                            truth_config: dict = {}
                            for key in REQUIRED_TRUTH_CONFIGS:
                                truth_config[key] = config[key]
                                del config[key]
                            truth_config["config"] = config
                            source_file.truth_configs[tc_key] = dataclass_from_dict(TruthConfig, truth_config)
                        for tc_key in source_file.truth_configs:
                            if (
                                "function" in truth_configs_merged[tc_key]
                                and truth_configs_merged[tc_key]["function"] == "file"
                            ):
                                truth_configs_merged[tc_key]["file"] = splitext(source_file.name)[0] + ".h5"
                    source_files.append(source_file)
            except Exception as e:
                raise OSError(f"Error processing {name}: {e}") from e

    return source_files


def get_ir_files(config: dict, show_progress: bool = False) -> list[ImpulseResponseFile]:
    """Get the list of impulse response files from a config

    :param config: Config dictionary
    :param show_progress: Show progress bar
    :return: List of impulse response files
    """
    from itertools import chain

    from ..utils.parallel import par_track
    from ..utils.parallel import track

    ir_files = list(
        chain.from_iterable(
            [
                append_ir_files(
                    entry=ImpulseResponseFile(
                        name=entry["name"],
                        tags=entry.get("tags", []),
                        delay=entry.get("delay", "auto"),
                    )
                )
                for entry in config["impulse_responses"]
            ]
        )
    )

    if len(ir_files) == 0:
        return []

    progress = track(total=len(ir_files), disable=not show_progress)
    ir_files = par_track(_get_ir_delay, ir_files, progress=progress)
    progress.close()

    return ir_files


def append_ir_files(entry: ImpulseResponseFile, tokens: dict | None = None) -> list[ImpulseResponseFile]:
    """Process impulse response files list and append as needed

    :param entry: Impulse response file entry to append to the list
    :param tokens: Tokens used for variable expansion
    :return: List of impulse response files
    """
    from glob import glob
    from os import listdir
    from os.path import dirname
    from os.path import isabs
    from os.path import isdir
    from os.path import join
    from os.path import splitext

    from ..utils.tokenized_shell_vars import tokenized_expand
    from ..utils.tokenized_shell_vars import tokenized_replace
    from .audio import validate_input_file

    if tokens is None:
        tokens = {}

    in_name, new_tokens = tokenized_expand(entry.name)
    tokens.update(new_tokens)
    names = sorted(glob(in_name))
    if not names:
        raise OSError(f"Could not find {in_name}. Make sure path exists")

    ir_files: list[ImpulseResponseFile] = []
    for name in names:
        ext = splitext(name)[1].lower()
        dir_name = dirname(name)
        if isdir(name):
            for file in listdir(name):
                if not isabs(file):
                    file = join(dir_name, file)
                child = ImpulseResponseFile(file, entry.tags, entry.delay)
                ir_files.extend(append_ir_files(entry=child, tokens=tokens))
        else:
            try:
                if ext == ".txt":
                    with open(file=name) as txt_file:
                        for line in txt_file:
                            # strip comments
                            file = line.partition("#")[0]
                            file = file.rstrip()
                            if file:
                                file, new_tokens = tokenized_expand(file)
                                tokens.update(new_tokens)
                                if not isabs(file):
                                    file = join(dir_name, file)
                                child = ImpulseResponseFile(file, entry.tags, entry.delay)
                                ir_files.extend(append_ir_files(entry=child, tokens=tokens))
                elif ext == ".yml":
                    try:
                        yml_config = raw_load_config(name)

                        if "impulse_responses" in yml_config:
                            for record in yml_config["impulse_responses"]:
                                ir_files.extend(append_ir_files(entry=record, tokens=tokens))
                    except Exception as e:
                        raise OSError(f"Error processing {name}: {e}") from e
                else:
                    validate_input_file(name)
                    ir_files.append(ImpulseResponseFile(tokenized_replace(name, tokens), entry.tags, entry.delay))
            except Exception as e:
                raise OSError(f"Error processing {name}: {e}") from e

    return ir_files


def get_spectral_masks(config: dict) -> list[SpectralMask]:
    """Get the list of spectral masks from a config

    :param config: Config dictionary
    :return: List of spectral masks
    """
    from ..utils.dataclass_from_dict import list_dataclass_from_dict

    try:
        return list_dataclass_from_dict(list[SpectralMask], config["spectral_masks"])
    except Exception as e:
        raise ValueError(f"Error in spectral_masks: {e}") from e


def get_truth_parameters(config: dict) -> list[TruthParameter]:
    """Get the list of truth parameters from a config

    :param config: Config dictionary
    :return: List of truth parameters
    """
    from copy import deepcopy

    from . import truth_functions
    from .constants import REQUIRED_TRUTH_CONFIGS

    truth_parameters: list[TruthParameter] = []
    for category, source_config in config["sources"].items():
        if "truth_configs" in source_config:
            for truth_name, truth_config in source_config["truth_configs"].items():
                optional_config = deepcopy(truth_config)
                for key in REQUIRED_TRUTH_CONFIGS:
                    del optional_config[key]

                parameters = getattr(truth_functions, truth_config["function"] + "_parameters")(
                    config["feature"],
                    config["num_classes"],
                    optional_config,
                )
                truth_parameters.append(TruthParameter(category, truth_name, parameters))

    return truth_parameters


def _get_num_samples(entry: SourceFile) -> SourceFile:
    from .audio import get_num_samples

    entry.samples = get_num_samples(entry.name)
    return entry


def _get_ir_delay(entry: ImpulseResponseFile) -> ImpulseResponseFile:
    from .ir_delay import get_ir_delay

    if entry.delay == "auto":
        entry.delay = get_ir_delay(entry.name)
    else:
        try:
            entry.delay = int(entry.delay)
        except ValueError as e:
            raise ValueError(f"Invalid impulse response delay: {entry.delay}") from e

    return entry

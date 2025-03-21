"""sonusai genmixdb

usage: genmixdb [-hvmdjn] LOC

options:
    -h, --help
    -v, --verbose   Be verbose.
    -m, --mix       Save mixture data. [default: False].
    -d, --dryrun    Perform a dry run showing the processed config. [default: False].
    -j, --json      Save JSON version of database. [default: False].
    -n, --nopar     Do not run in parallel. [default: False].

Create mixture database data for training and evaluation. Optionally, also create mixture audio and feature/truth data.

genmixdb creates a database of training and evaluation feature and truth data generation information. It allows the
choice of audio neural-network feature types that are supported by the Aaware real-time front-end and truth data that is
synchronized frame-by-frame with the feature data.

For details, see sonusai doc.

"""

from sonusai.datatypes import Mixture
from sonusai.mixture import MixtureDatabase


def genmixdb(
    location: str,
    save_mix: bool = False,
    logging: bool = True,
    show_progress: bool = False,
    test: bool = False,
    save_json: bool = False,
    no_par: bool = False,
) -> None:
    from functools import partial
    from random import seed

    import pandas as pd
    import yaml

    from sonusai import logger
    from sonusai.constants import SAMPLE_BYTES
    from sonusai.constants import SAMPLE_RATE
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import generate_mixtures
    from sonusai.mixture import get_effect_rules
    from sonusai.mixture import get_ir_files
    from sonusai.mixture import get_source_files
    from sonusai.mixture import initialize_db
    from sonusai.mixture import load_config
    from sonusai.mixture import log_duration_and_sizes
    from sonusai.mixture import populate_class_label_table
    from sonusai.mixture import populate_class_weights_threshold_table
    from sonusai.mixture import populate_impulse_response_file_table
    from sonusai.mixture import populate_mixture_table
    from sonusai.mixture import populate_source_file_table
    from sonusai.mixture import populate_spectral_mask_table
    from sonusai.mixture import populate_top_table
    from sonusai.mixture import populate_truth_parameters_table
    from sonusai.mixture import update_mixid_width
    from sonusai.utils import human_readable_size
    from sonusai.utils import par_track
    from sonusai.utils import seconds_to_hms
    from sonusai.utils import track

    config = load_config(location)
    initialize_db(location, test)

    mixdb = MixtureDatabase(location, test)

    populate_top_table(location, config, test)
    populate_class_label_table(location, config, test)
    populate_class_weights_threshold_table(location, config, test)
    populate_spectral_mask_table(location, config, test)
    populate_truth_parameters_table(location, config, test)

    seed(config["seed"])

    if logging:
        logger.debug(f"Seed: {config['seed']}")
        logger.debug("Configuration:")
        logger.debug(yaml.dump(config))

    if logging:
        logger.info("Collecting sources")

    source_files = get_source_files(config, show_progress)
    logger.info("")

    if len([file for file in source_files if file.category == "primary"]) == 0:
        raise RuntimeError("Canceled due to no primary sources")

    populate_source_file_table(location, source_files, test)

    if logging:
        logger.info("Sources summary")
        data = {
            "category": [],
            "files": [],
            "size": [],
            "duration": [],
        }
        for category, source_files in mixdb.source_files.items():
            audio_samples = sum([source.samples for source in source_files])
            audio_duration = audio_samples / SAMPLE_RATE
            data["category"].append(category)
            data["files"].append(mixdb.num_source_files(category))
            data["size"].append(human_readable_size(audio_samples * SAMPLE_BYTES, 1))
            data["duration"].append(seconds_to_hms(seconds=audio_duration))

        df = pd.DataFrame(data)
        logger.info(df.to_string(index=False, header=False))
        logger.info("")

        for category, files in mixdb.source_files.items():
            logger.debug(f"List of {category} sources:")
            logger.debug(yaml.dump([file.name for file in files], default_flow_style=False))

    if logging:
        logger.info("Collecting impulse responses")

    ir_files = get_ir_files(config, show_progress=show_progress)
    logger.info("")

    populate_impulse_response_file_table(location, ir_files, test)

    if logging:
        logger.debug("List of impulse responses:")
        for idx, file in enumerate(ir_files):
            logger.debug(f"id: {idx}, name:{file.name}, delay: {file.delay}, tags: [{', '.join(file.tags)}]")
        logger.debug("")

    if logging:
        logger.info("Collecting effects")

    rules = get_effect_rules(location, config, test)

    if logging:
        logger.info("")
        for category, effect in rules.items():
            logger.debug(f"List of {category} rules:")
            logger.debug(yaml.dump([entry.to_dict() for entry in effect], default_flow_style=False))

    if logging:
        logger.debug("SNRS:")
        for category, source in config["sources"].items():
            if category != "primary":
                logger.debug(f"  {category}")
                for snr in source["snrs"]:
                    logger.debug(f"  - {snr}")
        logger.debug("")
        logger.debug("Mix Rules:")
        for category, source in config["sources"].items():
            if category != "primary":
                logger.debug(f"  {category}")
                for mix_rule in source["mix_rules"]:
                    logger.debug(f"  - {mix_rule}")
        logger.debug("")
        logger.debug("Spectral masks:")
        for spectral_mask in mixdb.spectral_masks:
            logger.debug(f"- {spectral_mask}")
        logger.debug("")

    if logging:
        logger.info("Generating mixtures")

    mixtures = generate_mixtures(location, config, rules, test)

    num_mixtures = len(mixtures)
    update_mixid_width(location, num_mixtures, test)

    if logging:
        logger.info(f"Found {num_mixtures:,} mixtures to process")

    total_duration = float(sum([mixture.samples for mixture in mixtures])) / SAMPLE_RATE

    if logging:
        log_duration_and_sizes(
            total_duration=total_duration,
            feature_step_samples=mixdb.feature_step_samples,
            feature_parameters=mixdb.feature_parameters,
            stride=mixdb.fg_stride,
            desc="Estimated",
        )
        logger.info(
            f"Feature shape:        "
            f"{mixdb.fg_stride} x {mixdb.feature_parameters} "
            f"({mixdb.fg_stride * mixdb.feature_parameters} total parameters)"
        )
        logger.info(f"Feature samples:      {mixdb.feature_samples} samples ({mixdb.feature_ms} ms)")
        logger.info(f"Feature step samples: {mixdb.feature_step_samples} samples ({mixdb.feature_step_ms} ms)")
        logger.info("")

    # Fill in the details
    if logging:
        logger.info("Processing mixtures")
    progress = track(total=num_mixtures, disable=not show_progress)
    mixtures = par_track(
        partial(
            _process_mixture,
            location=location,
            save_mix=save_mix,
            test=test,
        ),
        mixtures,
        progress=progress,
        no_par=no_par,
    )
    progress.close()

    populate_mixture_table(
        location=location,
        mixtures=mixtures,
        test=test,
        logging=logging,
        show_progress=show_progress,
    )

    total_duration = float(mixdb.total_samples() / SAMPLE_RATE)

    if logging:
        log_duration_and_sizes(
            total_duration=total_duration,
            feature_step_samples=mixdb.feature_step_samples,
            feature_parameters=mixdb.feature_parameters,
            stride=mixdb.fg_stride,
            desc="Actual",
        )
        logger.info("")

    if not test and save_json:
        if logging:
            logger.info(f"Writing JSON version of database to {location}")
        mixdb = MixtureDatabase(location)
        mixdb.save()


def _process_mixture(
    mixture: Mixture,
    location: str,
    save_mix: bool,
    test: bool,
) -> Mixture:
    from functools import partial

    from sonusai.mixture import update_mixture
    from sonusai.mixture import write_cached_data
    from sonusai.mixture import write_mixture_metadata

    mixdb = MixtureDatabase(location, test=test)
    mixture, genmix_data = update_mixture(mixdb, mixture, save_mix)

    write = partial(write_cached_data, location=location, name="mixture", index=mixture.name)

    if save_mix:
        write(
            items={
                "sources": genmix_data.sources,
                "source": genmix_data.source,
                "noise": genmix_data.noise,
                "mixture": genmix_data.mixture,
            }
        )

        write_mixture_metadata(mixdb, mixture=mixture)

    return mixture


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    import time
    from os import makedirs
    from os import remove
    from os.path import exists
    from os.path import isdir
    from os.path import join

    import yaml

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.mixture import load_config
    from sonusai.utils import seconds_to_hms

    verbose = args["--verbose"]
    save_mix = args["--mix"]
    dryrun = args["--dryrun"]
    save_json = args["--json"]
    no_par = args["--nopar"]
    location = args["LOC"]

    start_time = time.monotonic()

    if exists(location) and not isdir(location):
        remove(location)

    makedirs(location, exist_ok=True)

    create_file_handler(join(location, "genmixdb.log"))
    update_console_handler(verbose)
    initial_log_messages("genmixdb")

    if dryrun:
        config = load_config(location)
        logger.info("Dryrun configuration:")
        logger.info(yaml.dump(config))
        return

    logger.info(f"Creating mixture database for {location}")
    logger.info("")

    genmixdb(
        location=location,
        save_mix=save_mix,
        show_progress=True,
        save_json=save_json,
        no_par=no_par,
    )

    end_time = time.monotonic()
    logger.info(f"Completed in {seconds_to_hms(seconds=end_time - start_time)}")
    logger.info("")


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)

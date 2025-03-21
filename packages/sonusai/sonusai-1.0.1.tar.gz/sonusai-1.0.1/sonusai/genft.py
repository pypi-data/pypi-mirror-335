"""sonusai genft

usage: genft [-hvsn] [-i MIXID] LOC

options:
    -h, --help
    -v, --verbose               Be verbose.
    -i MIXID, --mixid MIXID     Mixture ID(s) to generate. [default: *].
    -s, --segsnr                Save segsnr. [default: False].
    -n, --nopar                 Do not run in parallel. [default: False].

Generate SonusAI feature/truth data from a SonusAI mixture database.

Inputs:
    LOC         A SonusAI mixture database directory.
    MIXID       A glob of mixture ID(s) to generate.

Outputs the following to the mixture database directory:
    <id>
        feature.pkl
        truth_f.pkl
        segsnr.pkl (optional)
        metadata.txt
    genft.log

"""

from sonusai.datatypes import GeneralizedIDs
from sonusai.datatypes import GenFTData


def genft(
    location: str,
    mixids: GeneralizedIDs = "*",
    compute_truth: bool = True,
    compute_segsnr: bool = False,
    cache: bool = False,
    show_progress: bool = False,
    force: bool = True,
    no_par: bool = False,
) -> list[GenFTData]:
    from functools import partial

    from sonusai.mixture import MixtureDatabase
    from sonusai.utils import par_track
    from sonusai.utils import track

    mixdb = MixtureDatabase(location)
    mixids = mixdb.mixids_to_list(mixids)

    progress = track(total=len(mixids), disable=not show_progress)
    results = par_track(
        partial(
            _genft_kernel,
            location=location,
            compute_truth=compute_truth,
            compute_segsnr=compute_segsnr,
            cache=cache,
            force=force,
        ),
        mixids,
        progress=progress,
        no_par=no_par,
    )
    progress.close()

    return results


def _genft_kernel(
    m_id: int,
    location: str,
    compute_truth: bool,
    compute_segsnr: bool,
    cache: bool,
    force: bool,
) -> GenFTData:
    from functools import partial
    from typing import Any

    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import write_cached_data
    from sonusai.mixture import write_mixture_metadata

    mixdb = MixtureDatabase(location)

    write_func = partial(write_cached_data, location=mixdb.location, name="mixture", index=mixdb.mixture(m_id).name)

    result = GenFTData()

    mixture = mixdb.mixture_mixture(m_id)

    feature, truth_f = mixdb.mixture_ft(m_id=m_id, mixture=mixture, force=force)
    result.feature = feature
    items: dict[str, Any] = {"feature": feature}

    if compute_truth:
        result.truth_f = truth_f
        items["truth_f"] = truth_f

    if compute_segsnr:
        segsnr_t = mixdb.mixture_segsnr_t(m_id)
        result.segsnr = mixdb.mixture_segsnr(m_id=m_id, segsnr_t=segsnr_t, force=force, cache=cache)

    if cache:
        write_func(items=items)
        write_mixture_metadata(mixdb, m_id=m_id)

    return result


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    import time
    from os.path import join

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.constants import SAMPLE_RATE
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import check_audio_files_exist
    from sonusai.utils import human_readable_size
    from sonusai.utils import seconds_to_hms

    verbose = args["--verbose"]
    mixids = args["--mixid"]
    compute_segsnr = args["--segsnr"]
    no_par = args["--nopar"]
    location = args["LOC"]

    start_time = time.monotonic()

    create_file_handler(join(location, "genft.log"))
    update_console_handler(verbose)
    initial_log_messages("genft")

    logger.info(f"Load mixture database from {location}")
    mixdb = MixtureDatabase(location)
    mixids = mixdb.mixids_to_list(mixids)

    total_samples = mixdb.total_samples(mixids)
    duration = total_samples / SAMPLE_RATE
    total_transform_frames = total_samples // mixdb.ft_config.overlap
    total_feature_frames = total_samples // mixdb.feature_step_samples

    logger.info("")
    logger.info(f"Found {len(mixids):,} mixtures to process")
    logger.info(
        f"{total_samples:,} samples, "
        f"{total_transform_frames:,} transform frames, "
        f"{total_feature_frames:,} feature frames"
    )

    check_audio_files_exist(mixdb)

    genft(
        location=location,
        mixids=mixids,
        compute_segsnr=compute_segsnr,
        cache=True,
        show_progress=True,
        no_par=no_par,
    )

    logger.info(f"Wrote {len(mixids)} mixtures to {location}")
    logger.info("")
    logger.info(f"Duration: {seconds_to_hms(seconds=duration)}")
    logger.info(
        f"feature:  {human_readable_size(total_feature_frames * mixdb.fg_stride * mixdb.feature_parameters * 4, 1)}"
    )
    logger.info(f"truth_f:  {human_readable_size(total_feature_frames * mixdb.num_classes * 4, 1)}")
    if compute_segsnr:
        logger.info(f"segsnr:   {human_readable_size(total_transform_frames * 4, 1)}")

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

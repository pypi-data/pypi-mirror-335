"""sonusai genmix

usage: genmix [-hvtsn] [-i MIXID] LOC

options:
    -h, --help
    -v, --verbose               Be verbose.
    -i MIXID, --mixid MIXID     Mixture ID(s) to generate. [default: *].
    -t, --truth                 Save truth_t. [default: False].
    -s, --segsnr                Save segsnr_t. [default: False].
    -n, --nopar                 Do not run in parallel. [default: False].

Create mixture data from a SonusAI mixture database.

Inputs:
    LOC         A SonusAI mixture database directory.
    MIXID       A glob of mixture ID(s) to generate.

Outputs the following to the mixture database directory:
    <id>
        metadata.txt
        sources.pkl
        source.pkl
        noise.pkl
        mixture.pkl
        truth_t.pkl (optional)
        segsnr_t.pkl (optional)
    genmix.log
"""

from sonusai.datatypes import GeneralizedIDs
from sonusai.datatypes import GenMixData


def genmix(
    location: str,
    mixids: GeneralizedIDs = "*",
    compute_truth: bool = False,
    compute_segsnr: bool = False,
    cache: bool = False,
    show_progress: bool = False,
    force: bool = True,
    no_par: bool = False,
) -> list[GenMixData]:
    from functools import partial

    from sonusai.mixture import MixtureDatabase
    from sonusai.utils import par_track
    from sonusai.utils import track

    mixdb = MixtureDatabase(location)
    mixids = mixdb.mixids_to_list(mixids)
    progress = track(total=len(mixids), disable=not show_progress)
    results = par_track(
        partial(
            _genmix_kernel,
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


def _genmix_kernel(
    m_id: int,
    location: str,
    compute_truth: bool,
    compute_segsnr: bool,
    cache: bool,
    force: bool,
) -> GenMixData:
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import write_mixture_metadata

    mixdb = MixtureDatabase(location)

    result = GenMixData()
    result.sources = mixdb.mixture_sources(m_id=m_id, force=force, cache=cache)
    result.source = mixdb.mixture_source(m_id=m_id, sources=result.sources, force=force, cache=cache)
    result.noise = mixdb.mixture_noise(m_id=m_id, sources=result.sources, force=force, cache=cache)
    result.mixture = mixdb.mixture_mixture(
        m_id=m_id,
        sources=result.sources,
        source=result.source,
        noise=result.noise,
        force=force,
        cache=cache,
    )

    if compute_truth:
        result.truth_t = mixdb.mixture_truth_t(m_id=m_id, force=force, cache=cache)

    if compute_segsnr:
        result.segsnr_t = mixdb.mixture_segsnr_t(
            m_id=m_id,
            sources=result.sources,
            source=result.source,
            noise=result.noise,
            force=force,
            cache=cache,
        )

    if cache:
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
    location = args["LOC"]
    mixids = args["--mixid"]
    compute_truth = args["--truth"]
    compute_segsnr = args["--segsnr"]
    no_par = args["--nopar"]

    start_time = time.monotonic()

    create_file_handler(join(location, "genmix.log"))
    update_console_handler(verbose)
    initial_log_messages("genmix")

    logger.info(f"Load mixture database from {location}")
    mixdb = MixtureDatabase(location)
    mixids = mixdb.mixids_to_list(mixids)

    total_samples = mixdb.total_samples(mixids)
    duration = total_samples / SAMPLE_RATE

    logger.info("")
    logger.info(f"Found {len(mixids):,} mixtures to process")
    logger.info(f"{total_samples:,} samples")

    check_audio_files_exist(mixdb)

    genmix(
        location=location,
        mixids=mixids,
        compute_truth=compute_truth,
        compute_segsnr=compute_segsnr,
        cache=True,
        show_progress=True,
        force=True,
        no_par=no_par,
    )

    logger.info(f"Wrote {len(mixids)} mixtures to {location}")
    logger.info("")
    logger.info(f"Duration: {seconds_to_hms(seconds=duration)}")
    logger.info(f"mixture:  {human_readable_size(total_samples * 2, 1)}")
    if compute_truth:
        logger.info(f"truth_t:  {human_readable_size(total_samples * mixdb.num_classes * 4, 1)}")
    logger.info(f"target:   {human_readable_size(total_samples * 2, 1)}")
    logger.info(f"noise:    {human_readable_size(total_samples * 2, 1)}")
    if compute_segsnr:
        logger.info(f"segsnr:   {human_readable_size(total_samples * 4, 1)}")

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

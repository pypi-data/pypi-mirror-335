"""sonusai genmetrics

usage: genmetrics [-hvusd] [-i MIXID] [-n INCLUDE] [-p NUMPROC] [-x EXCLUDE] LOC

options:
    -h, --help
    -v, --verbose                   Be verbose.
    -i MIXID, --mixid MIXID         Mixture ID(s) to generate. [default: *].
    -n INCLUDE, --include INCLUDE   Metrics to include. [default: all]
    -p NUMPROC, --nproc NUMPROC     Number of parallel processes to use. Default single thread.
    -x EXCLUDE, --exclude EXCLUDE   Metrics to exclude. [default: none]
    -u, --update                    Update metrics (do not regenerate existing metrics).
    -s, --supported                 Show list of supported metrics.
    -d, --dryrun                    Show list of metrics that will be generated and exit.

Calculate speech enhancement metrics of SonusAI mixture data in LOC.

Inputs:
    LOC         A SonusAI mixture database directory.
    MIXID       A glob of mixture ID(s) to generate.
    INCLUDE     Comma separated list of metrics to include. Can be "all" or
                any of the supported metrics or glob(s).
    EXCLUDE     Comma separated list of metrics to exclude. Can be "none" or
                any of the supported metrics or glob(s)

Note: The default include of "all" excludes the generation of ASR metrics,
i.e., "*asr*,*wer*". However, if include is manually specified to something other than "all",
then this behavior is overridden.

Similarly, the default exclude of "none" excludes the generation of ASR metrics,
i.e., "*asr*,*wer*". However, if exclude is manually specified to something other than "none",
then this behavior is also overridden.

Examples:

Generate all available mxwer metrics (as determined by mixdb asr_configs parameter):
> sonusai genmetrics -n"mxwer*" mixdb_loc

Generate only mxwer.faster metrics:
> sonusai genmetrics -n"mxwer.faster" mixdb_loc

Generate only faster metrics:
> sonusai genmetrics -n"*faster" mixdb_loc

Generate all available metrics except for mxcovl
> sonusai genmetrics -x"mxcovl" mixdb_loc

"""


def _process_mixture(mixid: int, location: str, metrics: list[str], update: bool = False) -> set[str]:
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import write_cached_data

    mixdb = MixtureDatabase(location)
    results = mixdb.mixture_metrics(m_id=mixid, metrics=metrics, force=not update)
    write_cached_data(mixdb.location, "mixture", mixdb.mixture(mixid).name, results)

    return set(results.keys())


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.mixture import MixtureDatabase
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    verbose = args["--verbose"]
    mixids = args["--mixid"]
    includes = {x.strip() for x in args["--include"].replace(" ", ",").lower().split(",") if x != ""}
    excludes = {x.strip() for x in args["--exclude"].replace(" ", ",").lower().split(",") if x != ""}
    update = args["--update"]
    show_supported = args["--supported"]
    dryrun = args["--dryrun"]
    num_proc = args["--nproc"]
    location = args["LOC"]

    import fnmatch
    import sys
    import time
    from functools import partial
    from os.path import join

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.utils import par_track
    from sonusai.utils import seconds_to_hms
    from sonusai.utils import track

    start_time = time.monotonic()

    # Setup logging file
    create_file_handler(join(location, "genmetrics.log"))
    update_console_handler(verbose)
    initial_log_messages("genmetrics")

    logger.info(f"Load mixture database from {location}")

    mixdb = MixtureDatabase(location)
    supported = mixdb.supported_metrics
    if show_supported:
        logger.info(f"\nSupported metrics:\n\n{supported.pretty}")
        sys.exit(0)

    # Handle default excludes
    if "none" in excludes:
        if "all" in includes:
            excludes = {"*asr*", "*wer*"}
        else:
            excludes = set()

    # Handle default includes
    if "all" in includes:
        includes = {"*"}

    included_metrics: set[str] = set()
    for include in includes:
        for m in fnmatch.filter(supported.names, include):
            included_metrics.add(m)

    excluded_metrics: set[str] = set()
    for exclude in excludes:
        for m in fnmatch.filter(supported.names, exclude):
            excluded_metrics.add(m)

    requested = included_metrics - excluded_metrics

    metrics = sorted(requested)

    if len(metrics) == 0:
        logger.warning("No metrics were requested")
        sys.exit(1)

    logger.info("Generating metrics:")
    logger.info(f"{', '.join(metrics)}")
    if dryrun:
        sys.exit(0)

    mixids = mixdb.mixids_to_list(mixids)
    logger.info("")
    logger.info(f"Found {len(mixids):,} mixtures to process")

    if num_proc is None or len(mixids) == 1:
        no_par = True
        num_proc = None
    else:
        no_par = False
        num_proc = int(num_proc)  # TBD add support for 'auto'

    progress = track(total=len(mixids), desc="genmetrics")
    results = par_track(
        partial(_process_mixture, location=location, metrics=metrics, update=update),
        mixids,
        progress=progress,
        num_cpus=num_proc,
        no_par=no_par,
    )
    progress.close()

    written_metrics = sorted(set().union(*results))
    logger.info(f"Wrote metrics for {len(mixids)} mixtures to {location}:")
    logger.info(f"{', '.join(written_metrics)}")
    logger.info("")

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

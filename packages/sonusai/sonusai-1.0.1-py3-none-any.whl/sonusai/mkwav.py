"""sonusai mkwav

usage: mkwav [-hvtsn] [-i MIXID] LOC

options:
    -h, --help
    -v, --verbose                   Be verbose.
    -i MIXID, --mixid MIXID         Mixture ID(s) to generate. [default: *].
    -t, --source                    Write source file.
    -s, --sources                   Write sources files.
    -n, --noise                     Write noise file.

The mkwav command creates WAV files from a SonusAI database.

Inputs:
    LOC         A SonusAI mixture database directory.
    MIXID       A glob of mixture ID(s) to generate.

Outputs the following to the mixture database directory:
    <id>
        mixture.wav:        mixture
        source.wav:         source (optional)
        source_<c>.wav:     source <category> (optional)
        noise.wav:          noise (optional)
        metadata.txt
    mkwav.log

"""


def _process_mixture(m_id: int, location: str, write_target: bool, write_targets: bool, write_noise: bool) -> None:
    from os import makedirs
    from os.path import join

    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import write_mixture_metadata
    from sonusai.utils import float_to_int16
    from sonusai.utils import write_audio

    mixdb = MixtureDatabase(location)

    index = mixdb.mixture(m_id).name
    location = join(mixdb.location, "mixture", index)
    makedirs(location, exist_ok=True)

    write_audio(name=join(location, "mixture.wav"), audio=float_to_int16(mixdb.mixture_mixture(m_id)))
    if write_target:
        write_audio(name=join(location, "source.wav"), audio=float_to_int16(mixdb.mixture_source(m_id)))
    if write_targets:
        for category, source in mixdb.mixture_sources(m_id).items():
            write_audio(name=join(location, f"sources_{category}.wav"), audio=float_to_int16(source))
    if write_noise:
        write_audio(name=join(location, "noise.wav"), audio=float_to_int16(mixdb.mixture_noise(m_id)))

    write_mixture_metadata(mixdb, m_id=m_id)


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    verbose = args["--verbose"]
    mixid = args["--mixid"]
    write_source = args["--source"]
    write_sources = args["--sources"]
    write_noise = args["--noise"]
    location = args["LOC"]

    import time
    from functools import partial
    from os.path import join

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import check_audio_files_exist
    from sonusai.utils import par_track
    from sonusai.utils import seconds_to_hms
    from sonusai.utils import track

    start_time = time.monotonic()

    create_file_handler(join(location, "mkwav.log"))
    update_console_handler(verbose)
    initial_log_messages("mkwav")

    logger.info(f"Load mixture database from {location}")
    mixdb = MixtureDatabase(location)
    mixid = mixdb.mixids_to_list(mixid)

    total_samples = mixdb.total_samples(mixid)

    logger.info("")
    logger.info(f"Found {len(mixid):,} mixtures to process")
    logger.info(f"{total_samples:,} samples")

    check_audio_files_exist(mixdb)

    progress = track(total=len(mixid))
    par_track(
        partial(
            _process_mixture,
            location=location,
            write_target=write_source,
            write_targets=write_sources,
            write_noise=write_noise,
        ),
        mixid,
        progress=progress,
        # no_par=True,
    )
    progress.close()

    logger.info(f"Wrote {len(mixid)} mixtures to {location}")
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

from functools import lru_cache

from ..datatypes import AudioT


def validate_sox_effects(effects: list[str]) -> None:
    import subprocess

    import numpy as np

    zeros = np.zeros((1, 100), dtype=np.float32)

    for effect in effects:
        name = effect.split()[0]
        if name not in list_sox_effects():
            raise ValueError(f"Effect {name} is not supported.")

    args_list = _build_sox_args(effects)

    for args in args_list:
        # print(f"Validating sox effects: {' '.join(args)}")

        process_handle = subprocess.Popen(  # noqa: S603
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = process_handle.communicate(zeros.T.tobytes(order="F"))
        stderr = stderr.decode("utf-8")
        status = process_handle.returncode

        if status != 0:
            raise ValueError(f"For sox effects: {' '.join(effects)}\n{stderr}")


def apply_sox_effects(audio: AudioT, effects: list[str]) -> AudioT:
    """Apply effects to audio data using sox

    :param audio: Audio
    :param effects: List of effects
    :return: Effected audio
    """
    import subprocess

    import numpy as np

    new_audio = audio.copy()

    args_list = _build_sox_args(effects)
    for args in args_list:
        # print(f"Applying sox effects: {' '.join(args)}")

        process_handle = subprocess.Popen(  # noqa: S603
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process_handle.communicate(new_audio.T.tobytes(order="F"))
        stderr = stderr.decode("utf-8")
        status = process_handle.returncode

        if status != 0:
            raise RuntimeError(stderr)

        old_samples = len(new_audio)
        new_audio = np.frombuffer(stdout, dtype=audio.dtype)

        # The length sometimes changes +/-1 with the 'pitch' effect;
        # force the output back to the original length
        new_samples = len(new_audio)
        if "pitch" in args:
            if abs(new_samples - old_samples) > 1:
                raise RuntimeError(
                    "Encountered unexpected length change during 'pitch' effect:\n"
                    + f"{' '.join(args)}\n"
                    + f"original length: {old_samples}, new length: {new_samples}"
                )
            if new_samples < old_samples:
                new_audio = np.pad(array=new_audio, pad_width=(0, old_samples - new_samples))
            elif new_samples > old_samples:
                new_audio = new_audio[:old_samples]

    return new_audio


def _build_sox_args(effects: list[str]) -> list[list[str]]:
    from shlex import split

    from ..constants import SAMPLE_RATE

    base_args = [
        "sox",
        "-D",  # don't dither automatically
        "-V2",  # set verbosity to warning
        "-t",  # set input file type
        "f32",
        "-r",  # set input sample rate
        SAMPLE_RATE,
        "-c",  # set input channels
        1,
        "-",
        "-t",  # set output file type
        "raw",
        "-r",  # set output sample rate
        SAMPLE_RATE,
        "-b",  # set output encoded sample size in bits
        32,
        "-c",  # set output channels
        1,
        "-",
    ]

    result: list[list[str]] = []
    args: list = []
    for effect in effects:
        # If this is a pitch effect and there were other effects already,
        # isolate those other effects and start a new chain
        if effect.startswith("pitch") and args:
            result.append([str(x) for x in base_args + args])
            args = []

        args.extend(split(effect))

        # If this is a pitch effect, finish isolating it as its own chain
        # This allows "fixing" the length after applying the effect
        if effect.startswith("pitch"):
            result.append([str(x) for x in base_args + args])
            args = []

    if args:
        result.append([str(x) for x in base_args + args])

    return result


@lru_cache
def list_sox_effects() -> list[str]:
    from inspect import getmembers
    from inspect import isfunction

    from . import sox_help

    return [member[0] for member in getmembers(sox_help, isfunction)]


def help_sox_effects(name: str) -> str:
    from . import sox_help

    if name not in list_sox_effects():
        raise ValueError(f"Effect {name} not supported.")

    return getattr(sox_help, name)()


def sox_stats(audio: AudioT, win_len: float | None = None) -> str:
    import subprocess

    from ..constants import SAMPLE_RATE

    args = [
        "sox",
        "-D",
        "-V2",
        "-t",
        "f32",
        "-r",
        SAMPLE_RATE,
        "-c",
        1,
        "-",
        "-n",
        "stats",
    ]

    if win_len is not None:
        args.extend(["-w", win_len])

    args = [str(x) for x in args]

    process_handle = subprocess.Popen(  # noqa: S603
        args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    _, stderr = process_handle.communicate(audio.T.tobytes(order="F"))
    stderr = stderr.decode("utf-8")
    status = process_handle.returncode

    if status != 0:
        raise RuntimeError(stderr)

    return stderr

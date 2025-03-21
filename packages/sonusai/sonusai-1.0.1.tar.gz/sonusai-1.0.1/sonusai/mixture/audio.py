from functools import lru_cache
from pathlib import Path

from ..datatypes import AudioT


def get_next_noise(audio: AudioT, offset: int, length: int) -> AudioT:
    """Get next sequence of noise data from noise audio

    :param audio: Overall noise audio (entire file's worth of data)
    :param offset: Starting sample
    :param length: Number of samples to get
    :return: Sequence of noise audio data
    """
    import numpy as np

    return np.take(audio, range(offset, offset + length), mode="wrap")


def get_duration(audio: AudioT) -> float:
    """Get duration of audio in seconds

    :param audio: Time domain data [samples]
    :return: Duration of audio in seconds
    """
    from ..constants import SAMPLE_RATE

    return len(audio) / SAMPLE_RATE


def validate_input_file(input_filepath: str | Path) -> None:
    from os.path import exists
    from os.path import splitext

    from soundfile import available_formats

    if not exists(input_filepath):
        raise OSError(f"input_filepath {input_filepath} does not exist.")

    ext = splitext(input_filepath)[1][1:].lower()
    read_formats = [item.lower() for item in available_formats()]
    if ext not in read_formats:
        raise OSError(f"This installation cannot process .{ext} files")


def get_sample_rate(name: str | Path, use_cache: bool = True) -> int:
    """Get sample rate from audio file

    :param name: File name
    :param use_cache: If true, use LRU caching
    :return: Sample rate
    """
    if use_cache:
        return _get_sample_rate(name)
    return _get_sample_rate.__wrapped__(name)


@lru_cache
def _get_sample_rate(name: str | Path) -> int:
    """Get sample rate from audio file using soundfile

    :param name: File name
    :return: Sample rate
    """
    import soundfile
    from pydub import AudioSegment

    from ..utils.tokenized_shell_vars import tokenized_expand

    expanded_name, _ = tokenized_expand(name)

    try:
        if expanded_name.endswith(".mp3"):
            return AudioSegment.from_mp3(expanded_name).frame_rate

        if expanded_name.endswith(".m4a"):
            return AudioSegment.from_file(expanded_name).frame_rate

        return soundfile.info(expanded_name).samplerate
    except Exception as e:
        if name != expanded_name:
            raise OSError(f"Error reading {name} (expanded: {expanded_name}): {e}") from e
        else:
            raise OSError(f"Error reading {name}: {e}") from e


def raw_read_audio(name: str | Path) -> tuple[AudioT, int]:
    import numpy as np
    import soundfile
    from pydub import AudioSegment

    from ..utils.tokenized_shell_vars import tokenized_expand

    expanded_name, _ = tokenized_expand(name)

    try:
        if expanded_name.endswith(".mp3"):
            sound = AudioSegment.from_mp3(expanded_name)
            raw = np.array(sound.get_array_of_samples()).astype(np.float32).reshape((-1, sound.channels))
            raw = raw / 2 ** (sound.sample_width * 8 - 1)
            sample_rate = sound.frame_rate
        elif expanded_name.endswith(".m4a"):
            sound = AudioSegment.from_file(expanded_name)
            raw = np.array(sound.get_array_of_samples()).astype(np.float32).reshape((-1, sound.channels))
            raw = raw / 2 ** (sound.sample_width * 8 - 1)
            sample_rate = sound.frame_rate
        else:
            raw, sample_rate = soundfile.read(expanded_name, always_2d=True, dtype="float32")
    except Exception as e:
        if name != expanded_name:
            raise OSError(f"Error reading {name} (expanded: {expanded_name}): {e}") from e
        else:
            raise OSError(f"Error reading {name}: {e}") from e

    return np.squeeze(raw[:, 0].astype(np.float32)), sample_rate


def read_audio(name: str | Path, use_cache: bool = True) -> AudioT:
    """Read audio data from a file

    :param name: File name
    :param use_cache: If true, use LRU caching
    :return: Array of time domain audio data
    """
    if use_cache:
        return _read_audio(name)
    return _read_audio.__wrapped__(name)


@lru_cache
def _read_audio(name: str | Path) -> AudioT:
    """Read audio data from a file using soundfile

    :param name: File name
    :return: Array of time domain audio data
    """
    from ..constants import SAMPLE_RATE
    from .resample import resample

    out, sample_rate = raw_read_audio(name)

    return resample(out, orig_sr=sample_rate, target_sr=SAMPLE_RATE)


def get_num_samples(name: str | Path, use_cache: bool = True) -> int:
    """Get the number of samples resampled to the SonusAI sample rate in the given file

    :param name: File name
    :param use_cache: If true, use LRU caching
    :return: number of samples in resampled audio
    """
    if use_cache:
        return _get_num_samples(name)
    return _get_num_samples.__wrapped__(name)


@lru_cache
def _get_num_samples(name: str | Path) -> int:
    """Get the number of samples resampled to the SonusAI sample rate in the given file

    :param name: File name
    :return: number of samples in resampled audio
    """
    import math

    import soundfile
    from pydub import AudioSegment

    from ..constants import SAMPLE_RATE
    from ..utils.tokenized_shell_vars import tokenized_expand

    expanded_name, _ = tokenized_expand(name)

    if expanded_name.endswith(".mp3"):
        sound = AudioSegment.from_mp3(expanded_name)
        samples = sound.frame_count()
        sample_rate = sound.frame_rate
    elif expanded_name.endswith(".m4a"):
        sound = AudioSegment.from_file(expanded_name)
        samples = sound.frame_count()
        sample_rate = sound.frame_rate
    else:
        info = soundfile.info(expanded_name)
        samples = info.frames
        sample_rate = info.samplerate

    return math.ceil(SAMPLE_RATE * samples / sample_rate)

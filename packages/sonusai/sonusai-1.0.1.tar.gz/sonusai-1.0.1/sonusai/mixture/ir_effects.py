from functools import lru_cache
from pathlib import Path

from ..datatypes import AudioT
from ..datatypes import ImpulseResponseData
from .audio import raw_read_audio


def apply_ir(audio: AudioT, ir: ImpulseResponseData) -> AudioT:
    """Apply impulse response to audio data using scipy

    :param audio: Audio
    :param ir: Impulse response data
    :return: Effected audio
    """
    import numpy as np
    from librosa import resample
    from scipy.signal import fftconvolve

    from ..constants import SAMPLE_RATE

    if not isinstance(audio, np.ndarray):
        raise TypeError("audio must be a numpy array")

    # Early exit if no ir or if all audio is zero
    if ir is None or not audio.any():
        return audio

    pk_in = np.max(np.abs(audio))

    # Convert audio to IR sample rate
    audio_in = resample(audio, orig_sr=SAMPLE_RATE, target_sr=ir.sample_rate, res_type="soxr_hq")

    # Apply IR
    audio_out = fftconvolve(audio_in, ir.data, mode="full")

    # Delay compensation
    audio_out = audio_out[ir.delay :]

    # Convert back to global sample rate
    audio_out = resample(audio_out, orig_sr=ir.sample_rate, target_sr=SAMPLE_RATE, res_type="soxr_hq")

    # Trim to length
    audio_out = audio_out[: len(audio)]

    # Gain compensation
    pk_out = np.max(np.abs(audio_out))
    pk_gain = pk_in / pk_out
    audio_out = audio_out * pk_gain

    return audio_out


def read_ir(name: str | Path, delay: int, use_cache: bool = True) -> ImpulseResponseData:
    """Read impulse response data

    :param name: File name
    :param delay: Delay in samples
    :param use_cache: If true, use LRU caching
    :return: ImpulseResponseData object
    """
    if use_cache:
        return _read_ir(name, delay)
    return _read_ir.__wrapped__(name, delay)


@lru_cache
def _read_ir(name: str | Path, delay: int) -> ImpulseResponseData:
    """Read impulse response data using soundfile

    :param name: File name
    :param delay: Delay in samples
    :return: ImpulseResponseData object
    """
    out, sample_rate = raw_read_audio(name)

    return ImpulseResponseData(data=out, sample_rate=sample_rate, delay=delay)

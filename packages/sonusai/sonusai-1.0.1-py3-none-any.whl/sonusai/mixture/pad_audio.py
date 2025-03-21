from ..datatypes import AudioT


def pad_audio_to_frame(audio: AudioT, frame_length: int = 1) -> AudioT:
    """Pad audio to be a multiple of frame length

    :param audio: Audio
    :param frame_length: Pad resulting audio to be a multiple of this
    :return: Padded audio
    """
    return pad_audio_to_length(audio, get_padded_length(len(audio), frame_length))


def get_padded_length(length: int, frame_length: int) -> int:
    """Get the number of pad samples needed

    :param length: Length of audio
    :param frame_length: Desired length will be a multiple of this
    :return: Padded length
    """
    mod = int(length % frame_length)
    pad_length = frame_length - mod if mod else 0
    return length + pad_length


def pad_audio_to_length(audio: AudioT, length: int) -> AudioT:
    """Pad audio to given length

    :param audio: Audio
    :param length: Length of output
    :return: Padded audio
    """
    import numpy as np

    return np.pad(array=audio, pad_width=(0, length - len(audio)))

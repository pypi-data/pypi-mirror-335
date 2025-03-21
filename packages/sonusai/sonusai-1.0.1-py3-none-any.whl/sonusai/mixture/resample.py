from ..datatypes import AudioT


def resample(audio: AudioT, orig_sr: int, target_sr: int) -> AudioT:
    from librosa import resample

    return resample(audio, orig_sr=orig_sr, target_sr=target_sr, res_type="soxr_hq")

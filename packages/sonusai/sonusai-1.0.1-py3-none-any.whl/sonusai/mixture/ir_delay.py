import numpy as np


def get_ir_delay(file: str) -> int:
    from ..utils.rand import seed_context
    from .audio import raw_read_audio

    ir, sample_rate = raw_read_audio(file)

    with seed_context(42):
        wgn_ref = np.random.normal(loc=0, scale=0.2, size=int(np.ceil(0.05 * sample_rate))).astype(np.float32)

    wgn_conv = np.convolve(ir, wgn_ref)

    return int(np.round(tdoa(wgn_conv, wgn_ref, interp=16, phat=True)))


def tdoa(signal: np.ndarray, reference: np.ndarray, interp: int = 1, phat: bool = False, fs: int | float = 1) -> float:
    """Estimates the shift of array signal with respect to reference using generalized cross-correlation.

    :param signal: The array whose tdoa is measured
    :param reference: The reference array
    :param interp: Interpolation factor for the output array
    :param phat: Apply the PHAT weighting
    :param fs: The sampling frequency of the input arrays
    :return: The estimated delay between the two arrays
    """
    n_reference = reference.shape[0]

    r_12 = correlate(signal, reference, interp=interp, phat=phat)

    delay = (np.argmax(np.abs(r_12)) / interp - (n_reference - 1)) / fs

    return float(delay)


def correlate(x1: np.ndarray, x2: np.ndarray, interp: int = 1, phat: bool = False) -> np.ndarray:
    """Compute the cross-correlation between x1 and x2

    :param x1: Input array 1
    :param x2: Input array 2
    :param interp: Interpolation factor for the output array
    :param phat: Apply the PHAT weighting
    :return: The cross-correlation between the two arrays
    """
    n_x1 = x1.shape[0]
    n_x2 = x2.shape[0]

    n = n_x1 + n_x2 - 1

    fft1 = np.fft.rfft(x1, n=n)
    fft2 = np.fft.rfft(x2, n=n)

    if phat:
        eps1 = np.mean(np.abs(fft1)) * 1e-10
        fft1 /= np.abs(fft1) + eps1
        eps2 = np.mean(np.abs(fft2)) * 1e-10
        fft2 /= np.abs(fft2) + eps2

    out = np.fft.irfft(fft1 * np.conj(fft2), n=int(n * interp))

    return np.concatenate([out[-interp * (n_x2 - 1) :], out[: (interp * n_x1)]])

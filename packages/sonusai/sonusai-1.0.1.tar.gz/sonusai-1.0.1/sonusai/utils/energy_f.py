from pyaaware import ForwardTransform

from ..datatypes import AudioF
from ..datatypes import AudioT
from ..datatypes import EnergyF


def compute_energy_f(
    frequency_domain: AudioF | None = None,
    time_domain: AudioT | None = None,
    transform: ForwardTransform | None = None,
) -> EnergyF:
    """Compute the energy in each bin

    Must provide either frequency domain or time domain input. If time domain input is provided, must also provide
    ForwardTransform object to use to convert to frequency domain.

    :param frequency_domain: Frequency domain data [frames, bins]
    :param time_domain: Time domain data [samples]
    :param transform: ForwardTransform object
    :return: Frequency domain per-bin energy data [frames, bins]
    """
    import numpy as np
    import torch

    if frequency_domain is None:
        if time_domain is None:
            raise ValueError("Must provide time or frequency domain input")
        if transform is None:
            raise ValueError("Must provide ForwardTransform object")

        _frequency_domain = transform.execute_all(torch.from_numpy(time_domain))[0].numpy()
    else:
        _frequency_domain = frequency_domain

    frames, bins = _frequency_domain.shape
    result = np.empty((frames, bins), dtype=np.float32)

    for f in range(frames):
        for b in range(bins):
            value = _frequency_domain[f, b]
            result[f, b] = np.real(value) * np.real(value) + np.imag(value) * np.imag(value)

    return result

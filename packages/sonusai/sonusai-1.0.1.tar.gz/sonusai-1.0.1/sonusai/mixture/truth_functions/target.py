from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def target_f_validate(_config: dict) -> None:
    pass


def target_f_parameters(feature: str, _num_classes: int, _config: dict) -> int:
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    ft = ForwardTransform(**feature_forward_transform_config(feature))

    if ft.ttype == "tdac-co":
        return ft.bins

    return ft.bins * 2


def target_f(mixdb: MixtureDatabase, m_id: int, category: str, _config: dict) -> Truth:
    """Frequency domain target truth function

    Calculates the true transform of the target using the STFT
    configuration defined by the feature. This will include a
    forward transform window if defined by the feature.

    Output shape: [:, 2 * bins] (target stacked real, imag) or
                  [:, bins] (target real only for tdac-co)
    """
    import torch
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    ft = ForwardTransform(**feature_forward_transform_config(mixdb.feature))

    target_audio = torch.from_numpy(mixdb.mixture_sources(m_id)[category])

    target_freq = ft.execute_all(target_audio)[0].numpy()
    return _stack_real_imag(target_freq, ft.ttype)


def target_mixture_f_validate(_config: dict) -> None:
    pass


def target_mixture_f_parameters(feature: str, _num_classes: int, _config: dict) -> int:
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    ft = ForwardTransform(**feature_forward_transform_config(feature))

    if ft.ttype == "tdac-co":
        return ft.bins * 2

    return ft.bins * 4


def target_mixture_f(mixdb: MixtureDatabase, m_id: int, category: str, _config: dict) -> Truth:
    """Frequency domain target and mixture truth function

    Calculates the true transform of the target and the mixture
    using the STFT configuration defined by the feature. This
    will include a forward transform window if defined by the
    feature.

    Output shape: [:, 4 * bins] (target stacked real, imag; mixture stacked real, imag) or
                  [:, 2 * bins] (target real; mixture real for tdac-co)
    """
    import numpy as np
    import torch
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    ft = ForwardTransform(**feature_forward_transform_config(mixdb.feature))

    target_audio = torch.from_numpy(mixdb.mixture_sources(m_id)[category])
    mixture_audio = torch.from_numpy(mixdb.mixture_mixture(m_id))

    target_freq = ft.execute_all(torch.from_numpy(target_audio))[0].numpy()
    mixture_freq = ft.execute_all(torch.from_numpy(mixture_audio))[0].numpy()

    frames, bins = target_freq.shape
    truth = np.empty((frames, bins * 4), dtype=np.float32)
    truth[:, : bins * 2] = _stack_real_imag(target_freq, ft.ttype)
    truth[:, bins * 2 :] = _stack_real_imag(mixture_freq, ft.ttype)
    return truth


def target_swin_f_validate(_config: dict) -> None:
    pass


def target_swin_f_parameters(feature: str, _num_classes: int, _config: dict) -> int:
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    return ForwardTransform(**feature_forward_transform_config(feature)).bins * 2


def target_swin_f(mixdb: MixtureDatabase, m_id: int, category: str, _config: dict) -> Truth:
    """Frequency domain target with synthesis window truth function

    Calculates the true transform of the target using the STFT
    configuration defined by the feature. This will include a
    forward transform window if defined by the feature and also
    the inverse transform (or synthesis) window.

    Output shape: [:, 2 * bins] (stacked real, imag)
    """
    import numpy as np
    import torch
    from pyaaware import ForwardTransform
    from pyaaware import InverseTransform
    from pyaaware import feature_forward_transform_config
    from pyaaware import feature_inverse_transform_config

    from ...utils.stacked_complex import stack_complex

    ft = ForwardTransform(**feature_forward_transform_config(mixdb.feature))
    it = InverseTransform(**feature_inverse_transform_config(mixdb.feature))

    target_audio = mixdb.mixture_sources(m_id)[category]

    truth = np.empty((len(target_audio) // ft.overlap, ft.bins * 2), dtype=np.float32)
    for idx, offset in enumerate(range(0, len(target_audio), ft.overlap)):
        audio_frame = torch.from_numpy(np.multiply(target_audio[offset : offset + ft.overlap], it.window))
        target_freq = ft.execute(audio_frame)[0].numpy()
        truth[idx] = stack_complex(target_freq)

    return truth


def _stack_real_imag(data: Truth, ttype: str) -> Truth:
    import numpy as np

    from ...utils.stacked_complex import stack_complex

    if ttype == "tdac-co":
        return np.real(data)

    return stack_complex(data)

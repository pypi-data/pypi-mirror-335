from ...datatypes import Truth
from ..mixdb import MixtureDatabase


def _core(mixdb: MixtureDatabase, m_id: int, category: str, parameters: int, polar: bool) -> Truth:
    import numpy as np
    import torch
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config
    from pyaaware import feature_inverse_transform_config

    source_audio = torch.from_numpy(mixdb.mixture_sources(m_id)[category])
    t_ft = ForwardTransform(**feature_forward_transform_config(mixdb.feature))
    n_ft = ForwardTransform(**feature_forward_transform_config(mixdb.feature))

    frames = t_ft.frames(source_audio)
    if mixdb.mixture(m_id).all_sources[category].snr_gain == 0:
        return np.zeros((frames, parameters), dtype=np.float32)

    noise_audio = torch.from_numpy(mixdb.mixture_noise(m_id))

    frame_size = feature_inverse_transform_config(mixdb.feature)["overlap"]

    frames = len(source_audio) // frame_size
    truth = np.empty((frames, t_ft.bins * 2), dtype=np.float32)
    for frame in range(frames):
        offset = frame * frame_size
        target_f = t_ft.execute(source_audio[offset : offset + frame_size])[0].numpy().astype(np.complex64)
        noise_f = n_ft.execute(noise_audio[offset : offset + frame_size])[0].numpy().astype(np.complex64)
        mixture_f = target_f + noise_f

        crm_data = np.empty(target_f.shape, dtype=np.complex64)
        with np.nditer(target_f, flags=["multi_index"], op_flags=[["readwrite"]]) as it:
            for _ in it:
                num = target_f[it.multi_index]
                den = mixture_f[it.multi_index]
                if num == 0:
                    crm_data[it.multi_index] = 0
                elif den == 0:
                    crm_data[it.multi_index] = complex(np.inf, np.inf)
                else:
                    crm_data[it.multi_index] = num / den

        truth[frame, : t_ft.bins] = np.absolute(crm_data) if polar else np.real(crm_data)
        truth[frame, t_ft.bins :] = np.angle(crm_data) if polar else np.imag(crm_data)

    return truth


def crm_validate(_config: dict) -> None:
    pass


def crm_parameters(feature: str, _num_classes: int, _config: dict) -> int:
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    return ForwardTransform(**feature_forward_transform_config(feature)).bins * 2


def crm(mixdb: MixtureDatabase, m_id: int, category: str, _config: dict) -> Truth:
    """Complex ratio mask truth generation function

    Calculates the true complex ratio mask (CRM) truth which is a complex number
    per bin = Mr + j*Mi. For a given noisy STFT bin value Y, it is used as

    (Mr*Yr + Mi*Yi) / (Yr^2 + Yi^2) + j*(Mi*Yr - Mr*Yi)/ (Yr^2 + Yi^2)

    Output shape: [:, 2 * bins]
    """
    return _core(
        mixdb=mixdb,
        m_id=m_id,
        category=category,
        parameters=crm_parameters(mixdb.feature, mixdb.num_classes, _config),
        polar=False,
    )


def crmp_validate(_config: dict) -> None:
    pass


def crmp_parameters(feature: str, _num_classes: int, _config: dict) -> int:
    from pyaaware import ForwardTransform
    from pyaaware import feature_forward_transform_config

    return ForwardTransform(**feature_forward_transform_config(feature)).bins * 2


def crmp(mixdb: MixtureDatabase, m_id: int, category: str, _config: dict) -> Truth:
    """Complex ratio mask polar truth generation function

    Same as the crm function except the results are magnitude and phase
    instead of real and imaginary.

    Output shape: [:, bins]
    """
    return _core(
        mixdb=mixdb,
        m_id=m_id,
        category=category,
        parameters=crmp_parameters(mixdb.feature, mixdb.num_classes, _config),
        polar=True,
    )

from pyaaware import ForwardTransform
from pyaaware import InverseTransform

from ..datatypes import AudioF
from ..datatypes import AudioT
from ..datatypes import EnergyT
from ..datatypes import FeatureGeneratorConfig
from ..datatypes import FeatureGeneratorInfo
from ..datatypes import GeneralizedIDs
from ..datatypes import Mixture
from ..datatypes import Source
from ..datatypes import Sources
from ..datatypes import SpeechMetadata
from ..datatypes import TransformConfig
from .db_datatypes import MixtureRecord
from .db_datatypes import SourceRecord
from .mixdb import MixtureDatabase


def generic_ids_to_list(num_ids: int, ids: GeneralizedIDs = "*") -> list[int]:
    """Resolve generalized IDs to a list of integers

    :param num_ids: Total number of indices
    :param ids: Generalized IDs
    :return: List of ID integers
    """
    all_ids = list(range(num_ids))

    if isinstance(ids, str):
        if ids == "*":
            return all_ids

        try:
            result = eval(f"{all_ids}[{ids}]")  # noqa: S307
            if isinstance(result, list):
                return result
            else:
                return [result]
        except NameError as e:
            raise ValueError(f"Empty ids {ids}: {e}") from e

    if isinstance(ids, range):
        result = list(ids)
    elif isinstance(ids, int):
        result = [ids]
    else:
        result = ids

    if not all(isinstance(x, int) and 0 <= x < num_ids for x in result):
        raise ValueError(f"Invalid entries in ids of {ids}")

    if not result:
        raise ValueError(f"Empty ids {ids}")

    return result


def get_feature_generator_info(fg_config: FeatureGeneratorConfig) -> FeatureGeneratorInfo:
    from pyaaware import FeatureGenerator

    from ..datatypes import TransformConfig

    fg = FeatureGenerator(feature_mode=fg_config.feature_mode)

    return FeatureGeneratorInfo(
        decimation=fg.decimation,
        stride=fg.stride,
        step=fg.step,
        feature_parameters=fg.feature_parameters,
        ft_config=TransformConfig(
            length=fg.ftransform_length,
            overlap=fg.ftransform_overlap,
            bin_start=fg.bin_start,
            bin_end=fg.bin_end,
            ttype=fg.ftransform_ttype,
        ),
        eft_config=TransformConfig(
            length=fg.eftransform_length,
            overlap=fg.eftransform_overlap,
            bin_start=fg.bin_start,
            bin_end=fg.bin_end,
            ttype=fg.eftransform_ttype,
        ),
        it_config=TransformConfig(
            length=fg.itransform_length,
            overlap=fg.itransform_overlap,
            bin_start=fg.bin_start,
            bin_end=fg.bin_end,
            ttype=fg.itransform_ttype,
        ),
    )


def mixture_all_speech_metadata(mixdb: MixtureDatabase, mixture: Mixture) -> dict[str, dict[str, SpeechMetadata]]:
    """Get a list of all speech metadata for the given mixture"""
    from praatio.utilities.constants import Interval

    from ..datatypes import SpeechMetadata

    results: dict[str, dict[str, SpeechMetadata]] = {}
    for category, source in mixture.all_sources.items():
        data: dict[str, SpeechMetadata] = {}
        for tier in mixdb.speaker_metadata_tiers:
            data[tier] = mixdb.speaker(mixdb.source_file(source.file_id).speaker_id, tier)

        for tier in mixdb.textgrid_metadata_tiers:
            item = get_textgrid_tier_from_source_file(mixdb.source_file(source.file_id).name, tier)
            if isinstance(item, list):
                # Check for tempo effect and adjust Interval start and end data as needed
                entries = []
                for entry in item:
                    entries.append(
                        Interval(
                            entry.start / source.pre_tempo,
                            entry.end / source.pre_tempo,
                            entry.label,
                        )
                    )
                data[tier] = entries
            else:
                data[tier] = item
        results[category] = data

    return results


def mixture_metadata(mixdb: MixtureDatabase, m_id: int | None = None, mixture: Mixture | None = None) -> str:
    """Create a string of metadata for a Mixture

    :param mixdb: Mixture database
    :param m_id: Mixture ID
    :param mixture: Mixture record
    :return: String of metadata
    """
    if m_id is not None:
        mixture = mixdb.mixture(m_id)

    if mixture is None:
        raise ValueError("No mixture specified.")

    metadata = ""
    speech_metadata = mixture_all_speech_metadata(mixdb, mixture)
    metadata += f"samples: {mixture.samples}\n"
    for category, source in mixture.all_sources.items():
        source_file = mixdb.source_file(source.file_id)
        metadata += f"{category} name: {source_file.name}\n"
        metadata += f"{category} effects: {source.effects.to_dict()}\n"
        metadata += f"{category} pre_tempo: {source.pre_tempo}\n"
        metadata += f"{category} class indices: {source_file.class_indices}\n"
        metadata += f"{category} start: {source.start}\n"
        metadata += f"{category} repeat: {source.repeat}\n"
        metadata += f"{category} snr: {source.snr}\n"
        metadata += f"{category} random_snr: {source.snr.is_random}\n"
        metadata += f"{category} snr_gain: {source.snr_gain}\n"
        for key in source_file.truth_configs:
            metadata += f"{category} truth '{key}' function: {source_file.truth_configs[key].function}\n"
            metadata += f"{category} truth '{key}' config:   {source_file.truth_configs[key].config}\n"
        for key in speech_metadata[category]:
            metadata += f"{category} speech {key}: {speech_metadata[category][key]}\n"

    return metadata


def write_mixture_metadata(mixdb: MixtureDatabase, m_id: int | None = None, mixture: Mixture | None = None) -> None:
    """Write mixture metadata to a text file

    :param mixdb: Mixture database
    :param m_id: Mixture ID
    :param mixture: Mixture record
    """
    from os.path import join

    if m_id is not None:
        name = mixdb.mixture(m_id).name
    elif mixture is not None:
        name = mixture.name
    else:
        raise ValueError("No mixture specified.")

    name = join(mixdb.location, "mixture", name, "metadata.txt")
    with open(file=name, mode="w") as f:
        f.write(mixture_metadata(mixdb, m_id, mixture))


def from_mixture(mixture: Mixture) -> tuple[str, int, int, int]:
    return mixture.name, mixture.samples, mixture.spectral_mask_id, mixture.spectral_mask_seed


def to_mixture(entry: MixtureRecord, sources: Sources) -> Mixture:
    return Mixture(
        name=entry.name,
        samples=entry.samples,
        all_sources=sources,
        spectral_mask_id=entry.spectral_mask_id,
        spectral_mask_seed=entry.spectral_mask_seed,
    )


def from_source(source: Source) -> tuple[str, int, float, bool, float, float, bool, int]:
    return (
        source.effects.to_json(),
        source.file_id,
        source.pre_tempo,
        source.repeat,
        source.snr,
        source.snr_gain,
        source.snr.is_random,
        source.start,
    )


def to_source(entry: SourceRecord) -> Source:
    import json

    from ..datatypes import Effects
    from ..datatypes import UniversalSNR
    from ..utils.dataclass_from_dict import dataclass_from_dict

    return Source(
        file_id=entry.file_id,
        effects=dataclass_from_dict(Effects, json.loads(entry.effects)),
        start=entry.start,
        repeat=entry.repeat,
        snr=UniversalSNR(entry.snr, entry.snr_random),
        snr_gain=entry.snr_gain,
        pre_tempo=entry.pre_tempo,
    )


def get_transform_from_audio(audio: AudioT, transform: ForwardTransform) -> tuple[AudioF, EnergyT]:
    """Apply forward transform to input audio data to generate transform data

    :param audio: Time domain data [samples]
    :param transform: ForwardTransform object
    :return: Frequency domain data [frames, bins], Energy [frames]
    """
    import torch

    f, e = transform.execute_all(torch.from_numpy(audio))

    return f.numpy(), e.numpy()


def forward_transform(audio: AudioT, config: TransformConfig) -> AudioF:
    """Transform time domain data into frequency domain using the forward transform config from the feature

    A new transform is used for each call; i.e., state is not maintained between calls to forward_transform().

    :param audio: Time domain data [samples]
    :param config: Transform configuration
    :return: Frequency domain data [frames, bins]
    """
    from pyaaware import ForwardTransform

    audio_f, _ = get_transform_from_audio(
        audio=audio,
        transform=ForwardTransform(
            length=config.length,
            overlap=config.overlap,
            bin_start=config.bin_start,
            bin_end=config.bin_end,
            ttype=config.ttype,
        ),
    )
    return audio_f


def get_audio_from_transform(data: AudioF, transform: InverseTransform) -> tuple[AudioT, EnergyT]:
    """Apply inverse transform to input transform data to generate audio data

    :param data: Frequency domain data [frames, bins]
    :param transform: InverseTransform object
    :return: Time domain data [samples], Energy [frames]
    """

    import torch

    t, e = transform.execute_all(torch.from_numpy(data))

    return t.numpy(), e.numpy()


def inverse_transform(transform: AudioF, config: TransformConfig) -> AudioT:
    """Transform frequency domain data into time domain using the inverse transform config from the feature

    A new transform is used for each call; i.e., state is not maintained between calls to inverse_transform().

    :param transform: Frequency domain data [frames, bins]
    :param config: Transform configuration
    :return: Time domain data [samples]
    """
    from pyaaware import InverseTransform

    audio, _ = get_audio_from_transform(
        data=transform,
        transform=InverseTransform(
            length=config.length,
            overlap=config.overlap,
            bin_start=config.bin_start,
            bin_end=config.bin_end,
            ttype=config.ttype,
            gain=1,
        ),
    )
    return audio


def check_audio_files_exist(mixdb: MixtureDatabase) -> None:
    """Walk through all the noise and target audio files in a mixture database ensuring that they exist"""
    from os.path import exists

    from ..utils.tokenized_shell_vars import tokenized_expand

    for source_files in mixdb.source_files.values():
        for source_file in source_files:
            file_name, _ = tokenized_expand(source_file.name)
            if not exists(file_name):
                raise OSError(f"Could not find {file_name}")


def get_textgrid_tier_from_source_file(source_file: str, tier: str) -> SpeechMetadata | None:
    from pathlib import Path

    from praatio import textgrid
    from praatio.utilities.constants import Interval

    from ..utils.tokenized_shell_vars import tokenized_expand

    textgrid_file = Path(tokenized_expand(source_file)[0]).with_suffix(".TextGrid")
    if not textgrid_file.exists():
        return None

    tg = textgrid.openTextgrid(str(textgrid_file), includeEmptyIntervals=False)

    if tier not in tg.tierNames:
        return None

    entries = tg.getTier(tier).entries
    if len(entries) > 1:
        return [entry for entry in entries if isinstance(entry, Interval)]

    if len(entries) == 1:
        return entries[0].label

    return None


def frames_from_samples(samples: int, step_samples: int) -> int:
    import numpy as np

    return int(np.ceil(samples / step_samples))

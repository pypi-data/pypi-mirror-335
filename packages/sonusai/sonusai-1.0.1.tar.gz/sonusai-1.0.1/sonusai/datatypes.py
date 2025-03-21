from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import NamedTuple
from typing import SupportsIndex
from typing import TypeAlias

import numpy as np
import numpy.typing as npt
from dataclasses_json import DataClassJsonMixin
from praatio.utilities.constants import Interval

AudioT: TypeAlias = npt.NDArray[np.float32]

Truth: TypeAlias = Any
TruthDict: TypeAlias = dict[str, Truth]
TruthsDict: TypeAlias = dict[str, TruthDict]
Segsnr: TypeAlias = npt.NDArray[np.float32]

AudioF: TypeAlias = npt.NDArray[np.complex64]

EnergyT: TypeAlias = npt.NDArray[np.float32]
EnergyF: TypeAlias = npt.NDArray[np.float32]

Feature: TypeAlias = npt.NDArray[np.float32]

Predict: TypeAlias = npt.NDArray[np.float32]

# Json type defined to maintain compatibility with DataClassJsonMixin
Json: TypeAlias = dict | list | str | int | float | bool | None


class DataClassSonusAIMixin(DataClassJsonMixin):
    def __str__(self):
        return f"{self.to_dict()}"

    # Override DataClassJsonMixin to remove dictionary keys with values of None
    def to_dict(self, encode_json=False) -> dict[str, Json]:
        def del_none(d):
            if isinstance(d, dict):
                for key, value in list(d.items()):
                    if value is None:
                        del d[key]
                    elif isinstance(value, dict):
                        del_none(value)
                    elif isinstance(value, list):
                        for item in value:
                            del_none(item)
            elif isinstance(d, list):
                for item in d:
                    del_none(item)
            return d

        return del_none(super().to_dict(encode_json))


@dataclass(frozen=True)
class TruthConfig(DataClassSonusAIMixin):
    function: str
    stride_reduction: str
    config: dict = field(default_factory=dict)

    def __hash__(self):
        return hash(self.to_json())

    def __eq__(self, other):
        return isinstance(other, TruthConfig) and hash(self) == hash(other)


TruthConfigs: TypeAlias = dict[str, TruthConfig]
TruthsConfigs: TypeAlias = dict[str, TruthConfigs]


NumberStr: TypeAlias = float | int | str
OptionalNumberStr: TypeAlias = NumberStr | None
OptionalListNumberStr: TypeAlias = list[NumberStr] | None


EffectList: TypeAlias = list[str]


@dataclass
class Effects(DataClassSonusAIMixin):
    pre: EffectList
    post: EffectList = field(default_factory=EffectList)


class UniversalSNRGenerator:
    def __init__(self, raw_value: float | str) -> None:
        self._raw_value = str(raw_value)
        self.is_random = isinstance(raw_value, str) and raw_value.startswith("sai_rand")

    @property
    def value(self) -> float:
        from sonusai.mixture.effects import evaluate_sai_random_float

        if self.is_random:
            return float(evaluate_sai_random_float(self._raw_value))
        return float(self._raw_value)


class UniversalSNR(float):
    def __new__(cls, value: float, is_random: bool = False):
        return float.__new__(cls, value)

    def __init__(self, value: float, is_random: bool = False) -> None:
        float.__init__(value)
        self._is_random = bool(is_random)

    @property
    def is_random(self) -> bool:
        return self._is_random


Speaker: TypeAlias = dict[str, str]


@dataclass
class SourceFile(DataClassSonusAIMixin):
    category: str
    class_indices: list[int]
    name: str
    samples: int
    truth_configs: TruthConfigs
    class_balancing_effect: EffectList | None = None
    id: int = -1
    level_type: str | None = None
    speaker_id: int | None = None

    @property
    def duration(self) -> float:
        from .constants import SAMPLE_RATE

        return self.samples / SAMPLE_RATE


@dataclass
class EffectedFile(DataClassSonusAIMixin):
    file_id: int
    effect_id: int


ClassCount: TypeAlias = list[int]

GeneralizedIDs: TypeAlias = str | int | list[int] | range


@dataclass(frozen=True)
class SpectralMask(DataClassSonusAIMixin):
    f_max_width: int
    f_num: int
    t_max_width: int
    t_num: int
    t_max_percent: int


@dataclass(frozen=True)
class TruthParameter(DataClassSonusAIMixin):
    category: str
    name: str
    parameters: int | None


@dataclass
class Source(DataClassSonusAIMixin):
    effects: Effects
    file_id: int
    pre_tempo: float = 1
    repeat: bool = False
    snr: UniversalSNR = field(default_factory=lambda: UniversalSNR(0))
    snr_gain: float = 0
    start: int = 0


Sources: TypeAlias = dict[str, Source]
SourcesAudioT: TypeAlias = dict[str, AudioT]
SourcesAudioF: TypeAlias = dict[str, AudioF]


@dataclass
class Mixture(DataClassSonusAIMixin):
    name: str
    samples: int
    all_sources: Sources
    spectral_mask_id: int
    spectral_mask_seed: int

    @property
    def all_source_ids(self) -> dict[str, int]:
        return {category: source.file_id for category, source in self.all_sources.items()}

    @property
    def sources(self) -> Sources:
        return {category: source for category, source in self.all_sources.items() if category != "noise"}

    @property
    def source_ids(self) -> dict[str, int]:
        return {category: source.file_id for category, source in self.sources.items()}

    @property
    def noise(self) -> Source:
        return self.all_sources["noise"]

    @property
    def noise_id(self) -> int:
        return self.noise.file_id

    @property
    def source_effects(self) -> dict[str, Effects]:
        return {category: source.effects for category, source in self.sources.items()}

    @property
    def noise_effects(self) -> Effects:
        return self.noise.effects

    @property
    def is_noise_only(self) -> bool:
        return self.noise.snr < -96

    @property
    def is_source_only(self) -> bool:
        return self.noise.snr > 96


@dataclass(frozen=True)
class TransformConfig:
    length: int
    overlap: int
    bin_start: int
    bin_end: int
    ttype: str


@dataclass(frozen=True)
class FeatureGeneratorConfig:
    feature_mode: str
    truth_parameters: dict[str, dict[str, int | None]]


@dataclass(frozen=True)
class FeatureGeneratorInfo:
    decimation: int
    stride: int
    step: int
    feature_parameters: int
    ft_config: TransformConfig
    eft_config: TransformConfig
    it_config: TransformConfig


ASRConfigs: TypeAlias = dict[str, dict[str, Any]]


@dataclass
class GenMixData:
    mixture: AudioT | None = None
    truth_t: TruthsDict | None = None
    segsnr_t: Segsnr | None = None
    sources: SourcesAudioT | None = None
    source: AudioT | None = None
    noise: AudioT | None = None


@dataclass
class GenFTData:
    feature: Feature | None = None
    truth_f: TruthsDict | None = None
    segsnr: Segsnr | None = None


@dataclass
class ImpulseResponseData:
    data: AudioT
    sample_rate: int
    delay: int


@dataclass
class ImpulseResponseFile(DataClassSonusAIMixin):
    name: str
    tags: list[str]
    delay: str | int = "auto"


@dataclass
class MixtureDatabaseConfig(DataClassSonusAIMixin):
    asr_configs: ASRConfigs
    class_balancing: bool
    class_labels: list[str]
    class_weights_threshold: list[float]
    feature: str
    ir_files: list[ImpulseResponseFile]
    mixtures: list[Mixture]
    num_classes: int
    source_files: dict[str, list[SourceFile]]
    spectral_masks: list[SpectralMask]


SpeechMetadata: TypeAlias = str | list[Interval] | None


class SnrFMetrics(NamedTuple):
    avg: float | None = None
    std: float | None = None
    db_avg: float | None = None
    db_std: float | None = None


class SnrFBinMetrics(NamedTuple):
    avg: np.ndarray | None = None
    std: np.ndarray | None = None
    db_avg: np.ndarray | None = None
    db_std: np.ndarray | None = None


class SpeechMetrics(NamedTuple):
    csig: float | None = None
    cbak: float | None = None
    covl: float | None = None


class AudioStatsMetrics(NamedTuple):
    dco: float | None = None
    min: float | None = None
    max: float | None = None
    pkdb: float | None = None
    lrms: float | None = None
    pkr: float | None = None
    tr: float | None = None
    cr: float | None = None
    fl: float | None = None
    pkc: float | None = None


@dataclass
class MetricDoc:
    category: str
    name: str
    description: str


class MetricDocs(list[MetricDoc]):
    def __init__(self, __iterable: Iterable[MetricDoc]) -> None:
        super().__init__(item for item in __iterable)

    def __setitem__(self, __key: SupportsIndex, __value: MetricDoc) -> None:  # type: ignore[override]
        super().__setitem__(__key, __value)

    def insert(self, __index: SupportsIndex, __object: MetricDoc) -> None:
        super().insert(__index, __object)

    def append(self, __object: MetricDoc) -> None:
        super().append(__object)

    def extend(self, __iterable: Iterable[MetricDoc]) -> None:
        if isinstance(__iterable, type(self)):
            super().extend(__iterable)
        else:
            super().extend(item for item in __iterable)

    @property
    def pretty(self) -> str:
        max_category_len = ((max([len(item.category) for item in self]) + 9) // 10) * 10
        max_name_len = 2 + ((max([len(item.name) for item in self]) + 1) // 2) * 2
        categories: list[str] = []
        for item in self:
            if item.category not in categories:
                categories.append(item.category)

        result = ""
        for category in categories:
            result += f"{category}\n"
            result += "-" * max_category_len + "\n"
            for item in [sub for sub in self if sub.category == category]:
                result += f"  {item.name:<{max_name_len}}{item.description}\n"
            result += "\n"

        return result

    @property
    def names(self) -> set[str]:
        return {item.name for item in self}

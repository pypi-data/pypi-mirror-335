from collections import namedtuple

SourceFileRecord = namedtuple(
    "SourceFileRecord",
    [
        "id",
        "category",
        "class_indices",
        "level_type",
        "name",
        "samples",
        "speaker_id",
    ],
)

TopRecord = namedtuple(
    "TopRecord",
    [
        "id",
        "class_balancing",
        "feature",
        "mixid_width",
        "num_classes",
        "seed",
        "speaker_metadata_tiers",
        "textgrid_metadata_tiers",
        "version",
    ],
)

ClassLabelRecord = namedtuple(
    "ClassLabelRecord",
    [
        "id",
        "label",
    ],
)

ClassWeightsThresholdRecord = namedtuple(
    "ClassWeightsThresholdRecord",
    [
        "id",
        "threshold",
    ],
)

ImpulseResponseFileRecord = namedtuple(
    "ImpulseResponseFileRecord",
    [
        "id",
        "delay",
        "name",
    ],
)

SpectralMaskRecord = namedtuple(
    "SpectralMaskRecord",
    [
        "id",
        "f_max_width",
        "f_num",
        "t_max_percent",
        "t_max_width",
        "t_num",
    ],
)

SourceRecord = namedtuple(
    "SourceRecord",
    [
        "id",
        "effects",
        "file_id",
        "pre_tempo",
        "repeat",
        "snr",
        "snr_gain",
        "snr_random",
        "start",
    ],
)

MixtureRecord = namedtuple(
    "MixtureRecord",
    [
        "id",
        "name",
        "samples",
        "spectral_mask_id",
        "spectral_mask_seed",
    ],
)

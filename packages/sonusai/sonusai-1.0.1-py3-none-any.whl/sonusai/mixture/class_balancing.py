from ..datatypes import EffectList
from ..datatypes import EffectedFile
from ..datatypes import File


def balance_sources(
    effected_sources: list[EffectedFile],
    files: list[File],
    effects: list[EffectList],
    class_balancing_effect: EffectList,
    num_classes: int,
    num_ir: int,
    mixups: list[int] | None = None,
) -> tuple[list[EffectedFile], list[EffectList]]:
    import math

    from .augmentation import get_mixups
    from .sources import get_augmented_target_ids_by_class

    first_cba_id = len(effects)

    if mixups is None:
        mixups = get_mixups(effects)

    for mixup in mixups:
        if mixup == 1:
            continue

        effected_sources_indices_by_class = get_augmented_target_ids_by_class(
            augmented_targets=effected_sources,
            targets=files,
            target_augmentations=effects,
            mixup=mixup,
            num_classes=num_classes,
        )

        largest = max([len(item) for item in effected_sources_indices_by_class])
        largest = math.ceil(largest / mixup) * mixup
        for es_indices in effected_sources_indices_by_class:
            additional_effects_needed = largest - len(es_indices)
            file_ids = sorted({effected_sources[at_index].file_id for at_index in es_indices})

            tfi_idx = 0
            for _ in range(additional_effects_needed):
                file_id = file_ids[tfi_idx]
                tfi_idx = (tfi_idx + 1) % len(file_ids)
                effect_id, effects = _get_unused_balancing_effect(
                    effected_sources=effected_sources,
                    files=files,
                    effects=effects,
                    class_balancing_effect=class_balancing_effect,
                    file_id=file_id,
                    mixup=mixup,
                    num_ir=num_ir,
                    first_cbe_id=first_cba_id,
                )
                effected_sources.append(EffectedFile(file_id=file_id, effect_id=effect_id))

    return effected_sources, effects


def _get_unused_balancing_effect(
    effected_sources: list[EffectedFile],
    files: list[File],
    effects: list[EffectList],
    class_balancing_effect: EffectList,
    file_id: int,
    mixup: int,
    num_ir: int,
    first_cbe_id: int,
) -> tuple[int, list[EffectList]]:
    """Get an unused balancing augmentation for a given target file index"""
    from dataclasses import asdict

    from .augmentation import get_augmentation_rules

    balancing_augmentations = [item for item in range(len(effects)) if item >= first_cbe_id]
    used_balancing_augmentations = [
        effected_source.effect_id
        for effected_source in effected_sources
        if effected_source.file_id == file_id and effected_source.effect_id in balancing_augmentations
    ]

    augmentation_indices = [
        item
        for item in balancing_augmentations
        if item not in used_balancing_augmentations and effects[item].mixup == mixup
    ]
    if len(augmentation_indices) > 0:
        return augmentation_indices[0], effects

    class_balancing_effect = get_class_balancing_effect(file=files[file_id], default_cbe=class_balancing_effect)
    new_effect = get_augmentation_rules(rules=asdict(class_balancing_effect), num_ir=num_ir)[0]
    new_effect.mixup = mixup
    effects.append(new_effect)
    return len(effects) - 1, effects


def get_class_balancing_effect(file: File, default_cbe: EffectList) -> EffectList:
    """Get the class balancing effect rule for the given target"""
    if file.class_balancing_effect is not None:
        return file.class_balancing_effect
    return default_cbe

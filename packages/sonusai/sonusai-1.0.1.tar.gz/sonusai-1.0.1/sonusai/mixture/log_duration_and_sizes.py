def log_duration_and_sizes(
    total_duration: float,
    feature_step_samples: int,
    feature_parameters: int,
    stride: int,
    desc: str,
) -> None:
    from .. import logger
    from ..constants import FLOAT_BYTES
    from ..constants import SAMPLE_BYTES
    from ..constants import SAMPLE_RATE
    from ..utils.human_readable_size import human_readable_size
    from ..utils.seconds_to_hms import seconds_to_hms

    total_samples = int(total_duration * SAMPLE_RATE)
    mixture_bytes = total_samples * SAMPLE_BYTES
    feature_bytes = total_samples / feature_step_samples * stride * feature_parameters * FLOAT_BYTES

    logger.info("")
    logger.info(f"{desc} duration:   {seconds_to_hms(seconds=total_duration)}")
    logger.info(f"{desc} sizes:")
    logger.info(f" mixture:             {human_readable_size(mixture_bytes, 1)}")
    logger.info(f" feature:             {human_readable_size(feature_bytes, 1)}")

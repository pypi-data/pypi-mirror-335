# ruff: noqa: S608
from .mixdb import MixtureDatabase
from ..datatypes import AudioT
from ..datatypes import Effects
from ..datatypes import GenMixData
from ..datatypes import ImpulseResponseFile
from ..datatypes import Mixture
from ..datatypes import Source
from ..datatypes import SourceFile
from ..datatypes import SourcesAudioT
from ..datatypes import UniversalSNRGenerator


def config_file(location: str) -> str:
    from os.path import join

    return join(location, "config.yml")


def initialize_db(location: str, test: bool = False) -> None:
    from .mixdb import db_connection

    con = db_connection(location=location, create=True, test=test)

    con.execute("""
    CREATE TABLE truth_config(
    id INTEGER PRIMARY KEY NOT NULL,
    config TEXT NOT NULL)
    """)

    con.execute("""
    CREATE TABLE truth_parameters(
    id INTEGER PRIMARY KEY NOT NULL,
    category TEXT NOT NULL,
    name TEXT NOT NULL,
    parameters INTEGER)
    """)

    con.execute("""
    CREATE TABLE source_file (
    id INTEGER PRIMARY KEY NOT NULL,
    category TEXT NOT NULL,
    class_indices TEXT,
    level_type TEXT NOT NULL,
    name TEXT NOT NULL,
    samples INTEGER NOT NULL,
    speaker_id INTEGER,
    FOREIGN KEY(speaker_id) REFERENCES speaker (id))
    """)

    con.execute("""
    CREATE TABLE ir_file (
    id INTEGER PRIMARY KEY NOT NULL,
    delay INTEGER NOT NULL,
    name TEXT NOT NULL)
    """)

    con.execute("""
    CREATE TABLE ir_tag (
    id INTEGER PRIMARY KEY NOT NULL,
    tag TEXT NOT NULL UNIQUE)
    """)

    con.execute("""
    CREATE TABLE ir_file_ir_tag (
    file_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    FOREIGN KEY(file_id) REFERENCES ir_file (id),
    FOREIGN KEY(tag_id) REFERENCES ir_tag (id))
    """)

    con.execute("""
    CREATE TABLE speaker (
    id INTEGER PRIMARY KEY NOT NULL,
    parent TEXT NOT NULL)
    """)

    con.execute("""
    CREATE TABLE top (
    id INTEGER PRIMARY KEY NOT NULL,
    asr_configs TEXT NOT NULL,
    class_balancing BOOLEAN NOT NULL,
    feature TEXT NOT NULL,
    mixid_width INTEGER NOT NULL,
    num_classes INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    speaker_metadata_tiers TEXT NOT NULL,
    textgrid_metadata_tiers TEXT NOT NULL,
    version INTEGER NOT NULL)
    """)

    con.execute("""
    CREATE TABLE class_label (
    id INTEGER PRIMARY KEY NOT NULL,
    label TEXT NOT NULL)
    """)

    con.execute("""
    CREATE TABLE class_weights_threshold (
    id INTEGER PRIMARY KEY NOT NULL,
    threshold FLOAT NOT NULL)
    """)

    con.execute("""
    CREATE TABLE spectral_mask (
    id INTEGER PRIMARY KEY NOT NULL,
    f_max_width INTEGER NOT NULL,
    f_num INTEGER NOT NULL,
    t_max_percent INTEGER NOT NULL,
    t_max_width INTEGER NOT NULL,
    t_num INTEGER NOT NULL)
    """)

    con.execute("""
    CREATE TABLE source_file_truth_config (
    source_file_id INTEGER NOT NULL,
    truth_config_id INTEGER NOT NULL,
    FOREIGN KEY(source_file_id) REFERENCES source_file (id),
    FOREIGN KEY(truth_config_id) REFERENCES truth_config (id))
    """)

    con.execute("""
    CREATE TABLE source (
    id INTEGER PRIMARY KEY NOT NULL,
    effects TEXT NOT NULL,
    file_id INTEGER NOT NULL,
    pre_tempo FLOAT NOT NULL,
    repeat BOOLEAN NOT NULL,
    snr FLOAT NOT NULL,
    snr_gain FLOAT NOT NULL,
    snr_random BOOLEAN NOT NULL,
    start INTEGER NOT NULL,
    FOREIGN KEY(file_id) REFERENCES source_file (id))
    """)

    con.execute("""
    CREATE TABLE mixture (
    id INTEGER PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    samples INTEGER NOT NULL,
    spectral_mask_id INTEGER NOT NULL,
    spectral_mask_seed INTEGER NOT NULL,
    FOREIGN KEY(spectral_mask_id) REFERENCES spectral_mask (id))
    """)

    con.execute("""
    CREATE TABLE mixture_source (
    mixture_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    FOREIGN KEY(mixture_id) REFERENCES mixture (id),
    FOREIGN KEY(source_id) REFERENCES source (id))
    """)

    con.commit()
    con.close()


def populate_top_table(location: str, config: dict, test: bool = False) -> None:
    """Populate top table"""
    import json

    from .constants import MIXDB_VERSION
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)
    con.execute(
        """
    INSERT INTO top (id, asr_configs, class_balancing, feature, mixid_width, num_classes,
    seed, speaker_metadata_tiers, textgrid_metadata_tiers, version)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            1,
            json.dumps(config["asr_configs"]),
            config["class_balancing"],
            config["feature"],
            0,
            config["num_classes"],
            config["seed"],
            "",
            "",
            MIXDB_VERSION,
        ),
    )
    con.commit()
    con.close()


def populate_class_label_table(location: str, config: dict, test: bool = False) -> None:
    """Populate class_label table"""
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)
    con.executemany(
        "INSERT INTO class_label (label) VALUES (?)",
        [(item,) for item in config["class_labels"]],
    )
    con.commit()
    con.close()


def populate_class_weights_threshold_table(location: str, config: dict, test: bool = False) -> None:
    """Populate class_weights_threshold table"""
    from .mixdb import db_connection

    class_weights_threshold = config["class_weights_threshold"]
    num_classes = config["num_classes"]

    if not isinstance(class_weights_threshold, list):
        class_weights_threshold = [class_weights_threshold]

    if len(class_weights_threshold) == 1:
        class_weights_threshold = [class_weights_threshold[0]] * num_classes

    if len(class_weights_threshold) != num_classes:
        raise ValueError(f"invalid class_weights_threshold length: {len(class_weights_threshold)}")

    con = db_connection(location=location, readonly=False, test=test)
    con.executemany(
        "INSERT INTO class_weights_threshold (threshold) VALUES (?)",
        [(item,) for item in class_weights_threshold],
    )
    con.commit()
    con.close()


def populate_spectral_mask_table(location: str, config: dict, test: bool = False) -> None:
    """Populate spectral_mask table"""
    from .config import get_spectral_masks
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)
    con.executemany(
        """
    INSERT INTO spectral_mask (f_max_width, f_num, t_max_percent, t_max_width, t_num) VALUES (?, ?, ?, ?, ?)
    """,
        [
            (
                item.f_max_width,
                item.f_num,
                item.t_max_percent,
                item.t_max_width,
                item.t_num,
            )
            for item in get_spectral_masks(config)
        ],
    )
    con.commit()
    con.close()


def populate_truth_parameters_table(location: str, config: dict, test: bool = False) -> None:
    """Populate truth_parameters table"""
    from .config import get_truth_parameters
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)
    con.executemany(
        """
    INSERT INTO truth_parameters (category, name, parameters) VALUES (?, ?, ?)
    """,
        [
            (
                item.category,
                item.name,
                item.parameters,
            )
            for item in get_truth_parameters(config)
        ],
    )
    con.commit()
    con.close()


def populate_source_file_table(location: str, files: list[SourceFile], test: bool = False) -> None:
    """Populate source file table"""
    import json
    from pathlib import Path

    from .mixdb import db_connection

    _populate_truth_config_table(location, files, test)
    _populate_speaker_table(location, files, test)

    con = db_connection(location=location, readonly=False, test=test)

    cur = con.cursor()
    textgrid_metadata_tiers: set[str] = set()
    for file in files:
        # Get TextGrid tiers for source file and add to collection
        tiers = _get_textgrid_tiers_from_source_file(file.name)
        for tier in tiers:
            textgrid_metadata_tiers.add(tier)

        # Get truth settings for file
        truth_config_ids: list[int] = []
        if file.truth_configs:
            for name, config in file.truth_configs.items():
                ts = json.dumps({"name": name} | config.to_dict())
                cur.execute(
                    "SELECT truth_config.id FROM truth_config WHERE ? = truth_config.config",
                    (ts,),
                )
                truth_config_ids.append(cur.fetchone()[0])

        # Get speaker_id for source file
        cur.execute(
            "SELECT speaker.id FROM speaker WHERE ? = speaker.parent",
            (Path(file.name).parent.as_posix(),),
        )
        result = cur.fetchone()
        speaker_id = None
        if result is not None:
            speaker_id = result[0]

        # Add entry
        cur.execute(
            """
            INSERT INTO source_file (category, class_indices, level_type, name, samples, speaker_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                file.category,
                json.dumps(file.class_indices),
                file.level_type,
                file.name,
                file.samples,
                speaker_id,
            ),
        )
        source_file_id = cur.lastrowid
        for truth_config_id in truth_config_ids:
            cur.execute(
                "INSERT INTO source_file_truth_config (source_file_id, truth_config_id) VALUES (?, ?)",
                (source_file_id, truth_config_id),
            )

    # Update textgrid_metadata_tiers in the top table
    con.execute(
        "UPDATE top SET textgrid_metadata_tiers=? WHERE ? = top.id",
        (json.dumps(sorted(textgrid_metadata_tiers)), 1),
    )

    con.commit()
    con.close()


def populate_impulse_response_file_table(location: str, files: list[ImpulseResponseFile], test: bool = False) -> None:
    """Populate impulse response file table"""
    from .mixdb import db_connection

    _populate_impulse_response_tag_table(location, files, test)

    con = db_connection(location=location, readonly=False, test=test)

    cur = con.cursor()
    for file in files:
        # Get tags for file
        tag_ids: list[int] = []
        for tag in file.tags:
            cur.execute(
                "SELECT ir_tag.id FROM ir_tag WHERE ? = ir_tag.tag",
                (tag,),
            )
            tag_ids.append(cur.fetchone()[0])

        cur.execute(
            "INSERT INTO ir_file (delay, name) VALUES (?, ?)",
            (
                file.delay,
                file.name,
            ),
        )

        file_id = cur.lastrowid
        for tag_id in tag_ids:
            cur.execute(
                "INSERT INTO ir_file_ir_tag (file_id, tag_id) VALUES (?, ?)",
                (file_id, tag_id),
            )

    con.commit()
    con.close()


def update_mixid_width(location: str, num_mixtures: int, test: bool = False) -> None:
    """Update the mixid width"""
    from ..utils.max_text_width import max_text_width
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)
    con.execute(
        "UPDATE top SET mixid_width=? WHERE ? = top.id",
        (max_text_width(num_mixtures), 1),
    )
    con.commit()
    con.close()


def generate_mixtures(
    location: str,
    config: dict,
    effects: dict[str, list[Effects]],
    test: bool = False,
) -> list[Mixture]:
    """Generate mixtures"""
    mixdb = MixtureDatabase(location, test)

    effected_sources: dict[str, list[tuple[SourceFile, Effects]]] = {}
    for category in mixdb.source_files:
        effected_sources[category] = []
        for file in mixdb.source_files[category]:
            for effect in effects[category]:
                effected_sources[category].append((file, effect))

    mixtures: list[Mixture] = []
    for noise_mix_rule in config["sources"]["noise"]["mix_rules"]:
        match noise_mix_rule["mode"]:
            case "exhaustive":
                func = _exhaustive_noise_mix
            case "non-exhaustive":
                func = _non_exhaustive_noise_mix
            case "non-combinatorial":
                func = _non_combinatorial_noise_mix
            case _:
                raise ValueError(f"invalid noise mix_rule mode: {noise_mix_rule['mode']}")

        mixtures.extend(
            func(
                location=location,
                config=config,
                effected_sources=effected_sources,
                test=test,
            )
        )

    return mixtures


def populate_mixture_table(
    location: str,
    mixtures: list[Mixture],
    test: bool = False,
    logging: bool = False,
    show_progress: bool = False,
) -> None:
    """Populate mixture table"""
    from .. import logger
    from ..utils.parallel import track
    from .helpers import from_mixture
    from .helpers import from_source
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)

    # Populate source table
    if logging:
        logger.info("Populating source table")
    sources: list[tuple[str, int, float, bool, float, float, bool, int]] = []
    for mixture in mixtures:
        for source in mixture.all_sources.values():
            entry = from_source(source)
            if entry not in sources:
                sources.append(entry)
    for source in track(sources, disable=not show_progress):
        con.execute(
            """
        INSERT INTO source (effects, file_id, pre_tempo, repeat, snr, snr_gain, snr_random, start)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            source,
        )

    con.commit()

    # Populate mixture table
    if logging:
        logger.info("Populating mixture table")
    for mixture in track(mixtures, disable=not show_progress):
        m_id = int(mixture.name)
        con.execute(
            """
            INSERT INTO mixture (id, name, samples, spectral_mask_id, spectral_mask_seed)
            VALUES (?, ?, ?, ?, ?)
            """,
            (m_id + 1, *from_mixture(mixture)),
        )

        for source in mixture.all_sources.values():
            source_id = con.execute(
                """
                SELECT source.id
                FROM source
                WHERE ? = source.effects
                AND ? = source.file_id
                AND ? = source.pre_tempo
                AND ? = source.repeat
                AND ? = source.snr
                AND ? = source.snr_gain
                AND ? = source.snr_random
                AND ? = source.start
            """,
                from_source(source),
            ).fetchone()[0]
            con.execute(
                "INSERT INTO mixture_source (mixture_id, source_id) VALUES (?, ?)",
                (m_id + 1, source_id),
            )

    con.commit()
    con.close()


def update_mixture(mixdb: MixtureDatabase, mixture: Mixture, with_data: bool = False) -> tuple[Mixture, GenMixData]:
    """Update mixture record with name, samples, and gains"""
    import numpy as np

    sources_audio: SourcesAudioT = {}
    post_audio: SourcesAudioT = {}
    for category in mixture.all_sources:
        mixture, sources_audio[category], post_audio[category] = _update_source(mixdb, mixture, category)

    mixture = _initialize_mixture_gains(mixdb, mixture, post_audio)

    mixture.name = f"{int(mixture.name):0{mixdb.mixid_width}}"

    if not with_data:
        return mixture, GenMixData()

    # Apply gains
    post_audio = {
        category: post_audio[category] * mixture.all_sources[category].snr_gain for category in mixture.all_sources
    }

    # Sum sources, noise, and mixture
    source_audio = np.sum([post_audio[category] for category in mixture.sources], axis=0)
    noise_audio = post_audio["noise"]
    mixture_audio = source_audio + noise_audio

    return mixture, GenMixData(
        sources=sources_audio,
        source=source_audio,
        noise=noise_audio,
        mixture=mixture_audio,
    )


def _update_source(mixdb: MixtureDatabase, mixture: Mixture, category: str) -> tuple[Mixture, AudioT, AudioT]:
    from .effects import apply_effects
    from .effects import conform_audio_to_length

    source = mixture.all_sources[category]
    org_audio = mixdb.read_source_audio(source.file_id)

    org_samples = len(org_audio)
    pre_audio = apply_effects(mixdb, org_audio, source.effects, pre=True, post=False)

    pre_samples = len(pre_audio)
    mixture.all_sources[category].pre_tempo = org_samples / pre_samples

    pre_audio = conform_audio_to_length(pre_audio, mixture.samples, source.repeat, source.start)

    post_audio = apply_effects(mixdb, pre_audio, source.effects, pre=False, post=True)
    if len(pre_audio) != len(post_audio):
        raise RuntimeError(f"post-truth effects changed length: {source.effects.post}")

    return mixture, pre_audio, post_audio


def _initialize_mixture_gains(mixdb: MixtureDatabase, mixture: Mixture, sources_audio: SourcesAudioT) -> Mixture:
    import numpy as np

    from ..utils.asl_p56 import asl_p56
    from ..utils.db import db_to_linear

    sources_energy: dict[str, float] = {}
    for category in mixture.all_sources:
        level_type = mixdb.source_file(mixture.all_sources[category].file_id).level_type
        match level_type:
            case "default":
                sources_energy[category] = float(np.mean(np.square(sources_audio[category])))
            case "speech":
                sources_energy[category] = asl_p56(sources_audio[category])
            case _:
                raise ValueError(f"Unknown level_type: {level_type}")

    # Initialize all gains to 1
    for category in mixture.all_sources:
        mixture.all_sources[category].snr_gain = 1

    # Resolve gains
    for category in mixture.all_sources:
        if mixture.is_noise_only and category != "noise":
            # Special case for zeroing out source data
            mixture.all_sources[category].snr_gain = 0
        elif mixture.is_source_only and category == "noise":
            # Special case for zeroing out noise data
            mixture.all_sources[category].snr_gain = 0
        elif category != "primary":
            if sources_energy["primary"] == 0:
                # Avoid divide-by-zero
                mixture.all_sources[category].snr_gain = 1
            else:
                mixture.all_sources[category].snr_gain = float(
                    np.sqrt(sources_energy["primary"] / sources_energy[category])
                ) / db_to_linear(mixture.all_sources[category].snr)

    # Normalize gains
    max_snr_gain = max([source.snr_gain for source in mixture.all_sources.values()])
    for category in mixture.all_sources:
        mixture.all_sources[category].snr_gain = mixture.all_sources[category].snr_gain / max_snr_gain

    # Check for clipping in mixture
    mixture_audio = np.sum(
        [sources_audio[category] * mixture.all_sources[category].snr_gain for category in mixture.all_sources], axis=0
    )
    max_abs_audio = float(np.max(np.abs(mixture_audio)))
    clip_level = db_to_linear(-0.25)
    if max_abs_audio > clip_level:
        gain_adjustment = clip_level / max_abs_audio
        for category in mixture.all_sources:
            mixture.all_sources[category].snr_gain *= gain_adjustment

    # To improve repeatability, round results
    for category in mixture.all_sources:
        mixture.all_sources[category].snr_gain = round(mixture.all_sources[category].snr_gain, ndigits=5)

    return mixture


def _exhaustive_noise_mix(
    location: str,
    config: dict,
    effected_sources: dict[str, list[tuple[SourceFile, Effects]]],
    test: bool = False,
) -> list[Mixture]:
    """Use every noise/effect with every source/effect+interferences/effect"""
    from random import randint

    import numpy as np

    from ..datatypes import Mixture
    from ..datatypes import UniversalSNR
    from .effects import effects_from_rules
    from .effects import estimate_effected_length

    mixdb = MixtureDatabase(location, test)
    snrs = get_all_snrs_from_config(config)

    m_id = 0
    mixtures: list[Mixture] = []
    for noise_file, noise_rule in effected_sources["noise"]:
        noise_start = 0
        noise_effect = effects_from_rules(mixdb, noise_rule)
        noise_length = estimate_effected_length(noise_file.samples, noise_effect)

        for primary_file, primary_rule in effected_sources["primary"]:
            primary_effect = effects_from_rules(mixdb, primary_rule)
            primary_length = estimate_effected_length(primary_file.samples, primary_effect, mixdb.feature_step_samples)

            for spectral_mask_id in range(len(config["spectral_masks"])):
                for snr in snrs["noise"]:
                    mixtures.append(
                        Mixture(
                            name=str(m_id),
                            all_sources={
                                "primary": Source(
                                    file_id=primary_file.id,
                                    effects=primary_effect,
                                ),
                                "noise": Source(
                                    file_id=noise_file.id,
                                    effects=noise_effect,
                                    start=noise_start,
                                    repeat=True,
                                    snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                                ),
                            },
                            samples=primary_length,
                            spectral_mask_id=spectral_mask_id + 1,
                            spectral_mask_seed=randint(0, np.iinfo("i").max),  # noqa: S311
                        )
                    )
                    noise_start = int((noise_start + primary_length) % noise_length)
                    m_id += 1

    return mixtures


def _non_exhaustive_noise_mix(
    location: str,
    config: dict,
    effected_sources: dict[str, list[tuple[SourceFile, Effects]]],
    test: bool = False,
) -> list[Mixture]:
    """Cycle through every source/effect+interferences/effect without necessarily using all
    noise/effect combinations (reduced data set).
    """
    from random import randint

    import numpy as np

    from ..datatypes import Mixture
    from ..datatypes import UniversalSNR
    from .effects import effects_from_rules
    from .effects import estimate_effected_length

    mixdb = MixtureDatabase(location, test)
    snrs = get_all_snrs_from_config(config)

    next_noise = NextNoise(mixdb, effected_sources["noise"])

    m_id = 0
    mixtures: list[Mixture] = []
    for primary_file, primary_rule in effected_sources["primary"]:
        primary_effect = effects_from_rules(mixdb, primary_rule)
        primary_length = estimate_effected_length(primary_file.samples, primary_effect, mixdb.feature_step_samples)

        for spectral_mask_id in range(len(config["spectral_masks"])):
            for snr in snrs["noise"]:
                noise_file_id, noise_effect, noise_start = next_noise.generate(primary_file.samples)

                mixtures.append(
                    Mixture(
                        name=str(m_id),
                        all_sources={
                            "primary": Source(
                                file_id=primary_file.id,
                                effects=primary_effect,
                            ),
                            "noise": Source(
                                file_id=noise_file_id,
                                effects=noise_effect,
                                start=noise_start,
                                repeat=True,
                                snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                            ),
                        },
                        samples=primary_length,
                        spectral_mask_id=spectral_mask_id + 1,
                        spectral_mask_seed=randint(0, np.iinfo("i").max),  # noqa: S311
                    )
                )
                m_id += 1

    return mixtures


def _non_combinatorial_noise_mix(
    location: str,
    config: dict,
    effected_sources: dict[str, list[tuple[SourceFile, Effects]]],
    test: bool = False,
) -> list[Mixture]:
    """Combine a source/effect+interferences/effect with a single cut of a noise/effect
    non-exhaustively (each source/effect+interferences/effect does not use each noise/effect).
    Cut has random start and loop back to beginning if end of noise/effect is reached.
    """
    from random import choice
    from random import randint

    import numpy as np

    from ..datatypes import Mixture
    from ..datatypes import UniversalSNR
    from .effects import effects_from_rules
    from .effects import estimate_effected_length

    mixdb = MixtureDatabase(location, test)
    snrs = get_all_snrs_from_config(config)

    m_id = 0
    noise_id = 0
    mixtures: list[Mixture] = []
    for primary_file, primary_rule in effected_sources["primary"]:
        primary_effect = effects_from_rules(mixdb, primary_rule)
        primary_length = estimate_effected_length(primary_file.samples, primary_effect, mixdb.feature_step_samples)

        for spectral_mask_id in range(len(config["spectral_masks"])):
            for snr in snrs["noise"]:
                noise_file, noise_rule = effected_sources["noise"][noise_id]
                noise_effect = effects_from_rules(mixdb, noise_rule)
                noise_length = estimate_effected_length(noise_file.samples, noise_effect)

                mixtures.append(
                    Mixture(
                        name=str(m_id),
                        all_sources={
                            "primary": Source(
                                file_id=primary_file.id,
                                effects=primary_effect,
                            ),
                            "noise": Source(
                                file_id=noise_file.id,
                                effects=noise_effect,
                                start=choice(range(noise_length)),  # noqa: S311
                                repeat=True,
                                snr=UniversalSNR(value=snr.value, is_random=snr.is_random),
                            ),
                        },
                        samples=primary_length,
                        spectral_mask_id=spectral_mask_id + 1,
                        spectral_mask_seed=randint(0, np.iinfo("i").max),  # noqa: S311
                    )
                )
                noise_id = (noise_id + 1) % len(effected_sources["noise"])
                m_id += 1

    return mixtures


class NextNoise:
    def __init__(self, mixdb: MixtureDatabase, effected_noises: list[tuple[SourceFile, Effects]]) -> None:
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        self.mixdb = mixdb
        self.effected_noises = effected_noises

        self.noise_start = 0
        self.noise_id = 0
        self.noise_effect = effects_from_rules(self.mixdb, self.noise_rule)
        self.noise_length = estimate_effected_length(self.noise_file.samples, self.noise_effect)

    @property
    def noise_file(self):
        return self.effected_noises[self.noise_id][0]

    @property
    def noise_rule(self):
        return self.effected_noises[self.noise_id][1]

    def generate(self, length: int) -> tuple[int, Effects, int]:
        from .effects import effects_from_rules
        from .effects import estimate_effected_length

        if self.noise_start + length > self.noise_length:
            # Not enough samples in current noise
            if self.noise_start == 0:
                raise ValueError("Length of primary audio exceeds length of noise audio")

            self.noise_start = 0
            self.noise_id = (self.noise_id + 1) % len(self.effected_noises)
            self.noise_effect = effects_from_rules(self.mixdb, self.noise_rule)
            self.noise_length = estimate_effected_length(self.noise_file.samples, self.noise_effect)
            noise_start = self.noise_start
        else:
            # Current noise has enough samples
            noise_start = self.noise_start
            self.noise_start += length

        return self.noise_file.id, self.noise_effect, noise_start


def get_all_snrs_from_config(config: dict) -> dict[str, list[UniversalSNRGenerator]]:
    snrs: dict[str, list[UniversalSNRGenerator]] = {}
    for category in config["sources"]:
        if category != "primary":
            snrs[category] = [UniversalSNRGenerator(snr) for snr in config["sources"][category]["snrs"]]
    return snrs


def _get_textgrid_tiers_from_source_file(file: str) -> list[str]:
    from pathlib import Path

    from praatio import textgrid

    from ..utils.tokenized_shell_vars import tokenized_expand

    textgrid_file = Path(tokenized_expand(file)[0]).with_suffix(".TextGrid")
    if not textgrid_file.exists():
        return []

    tg = textgrid.openTextgrid(str(textgrid_file), includeEmptyIntervals=False)

    return sorted(tg.tierNames)


def _populate_speaker_table(location: str, source_files: list[SourceFile], test: bool = False) -> None:
    """Populate speaker table"""
    import json
    from pathlib import Path

    import yaml

    from ..utils.tokenized_shell_vars import tokenized_expand
    from .mixdb import db_connection

    # Determine columns for speaker table
    all_parents = {Path(file.name).parent for file in source_files}
    speaker_parents = (parent for parent in all_parents if Path(tokenized_expand(parent / "speaker.yml")[0]).exists())

    speakers: dict[Path, dict[str, str]] = {}
    for parent in sorted(speaker_parents):
        with open(tokenized_expand(parent / "speaker.yml")[0]) as f:
            speakers[parent] = yaml.safe_load(f)

    new_columns: list[str] = []
    for keys in speakers:
        for column in speakers[keys]:
            new_columns.append(column)
    new_columns = sorted(set(new_columns))

    con = db_connection(location=location, readonly=False, test=test)

    for new_column in new_columns:
        con.execute(f"ALTER TABLE speaker ADD COLUMN {new_column} TEXT")

    # Populate speaker table
    speaker_rows: list[tuple[str, ...]] = []
    for key in speakers:
        entry = (speakers[key].get(column, None) for column in new_columns)
        speaker_rows.append((key.as_posix(), *entry))  # type: ignore[arg-type]

    column_ids = ", ".join(["parent", *new_columns])
    column_values = ", ".join(["?"] * (len(new_columns) + 1))
    con.executemany(f"INSERT INTO speaker ({column_ids}) VALUES ({column_values})", speaker_rows)

    con.execute("CREATE INDEX speaker_parent_idx ON speaker (parent)")

    # Update speaker_metadata_tiers in the top table
    tiers = [
        description[0]
        for description in con.execute("SELECT * FROM speaker").description
        if description[0] not in ("id", "parent")
    ]
    con.execute(
        "UPDATE top SET speaker_metadata_tiers=? WHERE ? = top.id",
        (json.dumps(tiers), 1),
    )

    if "speaker_id" in tiers:
        con.execute("CREATE INDEX speaker_speaker_id_idx ON source_file (speaker_id)")

    con.commit()
    con.close()


def _populate_truth_config_table(location: str, source_files: list[SourceFile], test: bool = False) -> None:
    """Populate truth_config table"""
    import json

    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)

    # Populate truth_config table
    truth_configs: list[str] = []
    for file in source_files:
        for name, config in file.truth_configs.items():
            ts = json.dumps({"name": name} | config.to_dict())
            if ts not in truth_configs:
                truth_configs.append(ts)
    con.executemany(
        "INSERT INTO truth_config (config) VALUES (?)",
        [(item,) for item in truth_configs],
    )

    con.commit()
    con.close()


def _populate_impulse_response_tag_table(location: str, files: list[ImpulseResponseFile], test: bool = False) -> None:
    """Populate ir_tag table"""
    from .mixdb import db_connection

    con = db_connection(location=location, readonly=False, test=test)

    con.executemany(
        "INSERT INTO ir_tag (tag) VALUES (?)",
        [(tag,) for tag in {tag for file in files for tag in file.tags}],
    )

    con.commit()
    con.close()

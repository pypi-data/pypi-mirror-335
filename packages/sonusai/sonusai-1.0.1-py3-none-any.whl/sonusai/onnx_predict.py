"""sonusai onnx_predict

usage: onnx_predict [-hvlwr] [--include GLOB] [-i MIXID] MODEL DATA ...

options:
    -h, --help
    -v, --verbose               Be verbose.
    -i MIXID, --mixid MIXID     Mixture ID(s) to generate if input is a mixture database. [default: *].
    --include GLOB              Search only files whose base name matches GLOB. [default: *.{wav,flac}].
    -w, --write-wav             Calculate inverse transform of prediction and write .wav files

Run prediction (inference) using an ONNX model on a SonusAI mixture dataset or audio files from a glob path.
The ONNX Runtime (ort) inference engine is used to execute the inference.

Inputs:
    MODEL       ONNX model .onnx file of a trained model (weights are expected to be in the file).
                The model must also include required Sonusai hyperparameters.  See theSonusai torchl_onnx command.

    DATA        A string which must be one of the following:
                1. Path to a single file.  The prediction data is written to <filename_predict.*> in same location.
                2. Path to a Sonusai Mixture Database directory.
                 - Sonusai mixture database directory, prediction files will be named mixid_predict.*
                 - MIXID will select a subset of mixture ids
                3. Directory with audio files found recursively within.  See GLOB audio file extensions below.
                4. Regex resolving to a list of files.
                 - Subdirectory containing audio files with extension
                 - Regex resolving to a list of audio files

                   generate feature and truth data if not found.

Note there are multiple ways to process model prediction over multiple audio data files:
1. TSE (timestep single extension): mixture transform frames are fit into the timestep dimension and the model run as
   a single inference call.  If batch_size is > 1 then run multiple mixtures in one call with shorter mixtures
   zero-padded to the size of the largest mixture.
2. TME (timestep multi-extension): mixture is split into multiple timesteps, i.e. batch[0] is starting timesteps, ...
   Note that batches are run independently, thus sequential state from one set of timesteps to the next will not be
   maintained, thus results for such models (i.e. conv, LSTMs, in the timestep dimension) would not match using
   TSE mode.

TBD not sure below make sense, need to continue ??
2. BSE (batch single extension): mixture transform frames are fit into the batch dimension. This make sense only if
   independent predictions are made on each frame w/o considering previous frames (timesteps=1) or there is no
   timestep dimension in the model (timesteps=0).
3. Classification

Outputs the following to opredict-<TIMESTAMP> directory:
    <id>
        predict.h5
    onnx_predict.log

"""


def process_path(path, ext_list: list[str] | None = None):
    """
    Check path which can be a single file, a subdirectory, or a regex
    return:
      - a list of files with matching extensions to any in ext_list provided (i.e. ['.wav', '.mp3', '.acc'])
      - the basedir of the path, if
    """
    import glob
    from os.path import abspath
    from os.path import commonprefix
    from os.path import dirname
    from os.path import isdir
    from os.path import isfile
    from os.path import join

    from sonusai.utils import braced_iglob

    if ext_list is None:
        ext_list = [".wav", ".WAV", ".flac", ".FLAC", ".mp3", ".aac"]

    # Check if the path is a single file, and return it as a list with the dirname
    if isfile(path):
        if any(path.endswith(ext) for ext in ext_list):
            basedir = dirname(path)  # base directory
            if not basedir:
                basedir = "./"
            return [path], basedir
        else:
            return [], []

    # Check if the path is a dir, recursively find all files any of the specified extensions, return file list and dir
    if isdir(path):
        matching_files = []
        for ext in ext_list:
            matching_files.extend(glob.glob(join(path, "**/*" + ext), recursive=True))
        return matching_files, path

    # Process as a regex, return list of filenames and basedir
    apath = abspath(path)  # join(abspath(path), "**", "*.{wav,flac,WAV}")
    matching_files = []
    for file in braced_iglob(pathname=apath, recursive=True):
        matching_files.append(file)
    if matching_files:
        basedir = commonprefix(matching_files)  # Find basedir
        return matching_files, basedir
    else:
        return [], []


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    verbose = args["--verbose"]
    wav = args["--write-wav"]
    mixids = args["--mixid"]
    include = args["--include"]
    model_path = args["MODEL"]
    data_paths = args["DATA"]

    # Quick check of CPU and GPU devices
    import re
    import subprocess
    import time
    from os import makedirs
    from os.path import basename
    from os.path import exists
    from os.path import isdir
    from os.path import isfile
    from os.path import join
    from os.path import normpath
    from os.path import splitext

    import h5py
    import numpy as np
    import onnxruntime as ort
    import psutil

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.mixture import MixtureDatabase
    from sonusai.mixture import get_audio_from_feature
    from sonusai.utils import create_ts_name
    from sonusai.utils import load_ort_session
    from sonusai.utils import seconds_to_hms
    from sonusai.utils import write_audio

    num_cpu = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"#CPUs: {num_cpu}, current CPU utilization: {cpu_percent}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")

    vga_devices = [
        line.split(" ", 3)[-1]
        for line in subprocess.check_output("lspci | grep -i vga", shell=True).decode().splitlines()
    ]
    nv_devs = list(filter(lambda x: "nvidia" in x.lower(), vga_devices))
    nv_mods = [re.search(r"\[.*?\]", device).group(0) if re.search(r"\[.*?\]", device) else None for device in nv_devs]
    if len(nv_mods) > 0:
        print(f"{len(nv_mods)} Nvidia devices present: {nv_mods}")  # prints model names
    else:
        print("No cuda devices present, using cpu")

    avail_providers = ort.get_available_providers()
    print(f"Loaded ONNX Runtime, available providers: {avail_providers}.")
    if len(nv_mods) > 0:
        print(
            "If GPU is desired, need to replace onnxruntime with onnxruntime-gpu i.e. using pip:"
            "> pip uninstall onnxruntime"
            "> pip install onnxruntime-gpu\n\n"
        )

    # Quick check that model is valid
    if exists(model_path) and isfile(model_path):
        try:
            session = ort.InferenceSession(model_path)
            options = ort.SessionOptions()
        except Exception as e:
            print(f"Error: could not load ONNX model from {model_path}: {e}")
            raise SystemExit(1) from e
    else:
        print(f"Error: model file path is not valid: {model_path}")
        raise SystemExit(1)

    # Check datapath is valid
    if len(data_paths) == 1 and isdir(data_paths[0]):  # Try opening as mixdb subdir
        mixdb_path = data_paths[0]
        try:
            mixdb = MixtureDatabase(mixdb_path)
        except Exception:
            mixdb_path = None
        in_basename = basename(normpath(data_paths[0]))
        output_dir = create_ts_name("opredict-" + in_basename)
        num_featparams = mixdb.feature_parameters
        print(f"Loaded SonusAI mixdb with {mixdb.num_mixtures} mixtures and {num_featparams} classes")
        p_mixids = mixdb.mixids_to_list(mixids)
        feature_mode = mixdb.feature

    if mixdb_path is None:
        if verbose:
            print(f"Checking {len(data_paths)} locations ... ")
        # Check location, default ext are ['.wav', '.WAV', '.flac', '.FLAC', '.mp3', '.aac']
        pfiles, basedir = process_path(data_paths)
        if pfiles is None or len(pfiles) < 1:
            print(f"No audio files or Sonusai mixture database found in {data_paths}, exiting ...")
            raise SystemExit(1)
        else:
            pfiles = sorted(pfiles, key=basename)
            output_dir = basedir

    if mixdb_path is not None or len(pfiles) > 1:  # log file only if mixdb or more than one file
        makedirs(output_dir, exist_ok=True)
        # Setup logging file
        create_file_handler(join(output_dir, "onnx-predict.log"))
        update_console_handler(verbose)
        initial_log_messages("onnx_predict")
        # print some previous messages
        logger.info(f"Loaded ONNX Runtime, available providers: {avail_providers}.")
        if mixdb_path:
            logger.debug(f"Loaded SonusAI mixdb with {mixdb.num_mixtures} mixtures and {num_featparams} classes")
            if len(p_mixids) != mixdb.num_mixtures:
                logger.info(f"Processing a subset of {len(p_mixids)} from available mixtures.")

    # Reload model/session and do more thorough checking
    session, options, model_root, hparams, sess_inputs, sess_outputs = load_ort_session(model_path)
    if "CUDAExecutionProvider" in avail_providers:
        session.set_providers(["CUDAExecutionProvider"])
    if hparams is None:
        logger.error("Error: ONNX model does not have required SonusAI hyperparameters, cannot proceed.")
        raise SystemExit(1)

    if len(sess_inputs) != 1:  # TBD update to support state_in and state_out
        logger.error(f"Error: ONNX model does not have 1 input, but {len(sess_inputs)}. Exit due to unknown input.")

    in0name = sess_inputs[0].name
    in0type = sess_inputs[0].type
    in0shape = sess_inputs[0].shape  # a list
    # Check for 2 cases of model feature input shape:  batch x timesteps x fparams or batch x fparams
    if not isinstance(in0shape[0], str):
        model_batchsz = int(in0shape[0])
        logger.debug(f"Onnx model has fixed batch_size: {model_batchsz}.")
    else:
        model_batchsz = -1
        logger.debug("Onnx model has a dynamic batch_size.")

    if len(in0shape) < 3:
        model_tsteps = 0
        model_featparams = int(in0shape[1])
    else:
        model_featparams = int(in0shape[2])
        if not isinstance(in0shape[1], str):
            model_tsteps = int(in0shape[1])
            logger.debug(f"Onnx model has fixed timesteps: {model_tsteps}.")
        else:
            model_tsteps = -1
            logger.debug("Onnx model has dynamic timesteps dimension size.")

    out_names = [n.name for n in session.get_outputs()]

    if in0type.find("float16") != -1:
        model_is_fp16 = True
        logger.info("Detected input of float16, converting all feature inputs to that type.")
    else:
        model_is_fp16 = False

    logger.info(f"Read and compiled ONNX model from {model_path}.")

    start_time = time.monotonic()

    if mixdb is not None and hparams["batch_size"] == 1:
        if hparams["feature"] != feature_mode:  # warn on mis-match, but TBD could be sov-mode
            logger.warning("Mixture feature does not match model feature, this inference run may fail.")
        logger.info(f"Processing {len(p_mixids)} mixtures from SonusAI mixdb ...")
        logger.info(f"Using OnnxRT provider {session.get_providers()} ...")

        for mixid in p_mixids:
            # feature data is now always fp32 and frames x stride x feature_params
            feat_dat, _ = mixdb.mixture_ft(mixid)
            if feat_dat.shape[1] > 1:  # stride mode num_frames overrides batch dim, no reshape
                stride_mode = 1
                batch_size = feat_dat.shape[0]  # num_frames in stride mode becomes batch size
            if hparams["timesteps"] == 0:
                # no timestep dimension, remove the dimension
                timesteps = 0
                feat_dat = np.reshape(feat_dat, [batch_size, num_featparams])
            else:
                # fit frames into timestep dimension (TSE mode) and knowing batch_size = 1
                timesteps = feat_dat.shape[0]
                feat_dat = np.transpose(feat_dat, (1, 0, 2))  # transpose to 1 x frames=tsteps x feat_params

            if model_is_fp16:
                feat_dat = np.float16(feat_dat)  # type: ignore[assignment]

            # run inference, ort session wants i.e. batch x timesteps x feat_params, outputs numpy BxTxFP or BxFP
            predict = session.run(out_names, {in0name: feat_dat})[0]
            # predict, _ = reshape_outputs(predict=predict[0], timesteps=frames)  # frames x feat_params

            output_fname = join(output_dir, mixdb.mixture(mixid).name)
            with h5py.File(output_fname + ".h5", "a") as f:
                if "predict" in f:
                    del f["predict"]
                f.create_dataset("predict", data=predict)
            if wav:
                # note only makes sense if model is predicting audio, i.e., timestep dimension exists
                # predict_audio wants [frames, channels, feature_parameters] equivalent to timesteps, batch, bins
                predict = np.transpose(predict, [1, 0, 2])
                predict_audio = get_audio_from_feature(feature=predict, feature_mode=feature_mode)
                owav_name = splitext(output_fname)[0] + "_predict.wav"
                write_audio(owav_name, predict_audio)

    else:  # TBD add support
        logger.info("Mixture database does not exist or batch_size is not equal to one, exiting ...")

    end_time = time.monotonic()
    logger.info(f"Completed in {seconds_to_hms(seconds=end_time - start_time)}")
    logger.info("")


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)

    # mixdb_path = None
    # mixdb: MixtureDatabase | None = None
    # p_mixids: list[int] = []
    # entries: list[PathInfo] = []
    #
    # if len(data_paths) == 1 and isdir(data_paths[0]):
    #     # Assume it's a single path to SonusAI mixdb subdir
    #     in_basename = basename(normpath(data_paths[0]))
    #     mixdb_path = data_paths[0]
    # else:
    #     # search all data paths for .wav, .flac (or whatever is specified in include)
    #     in_basename = ""

    # if mixdb_path is not None:  # a mixdb is found and loaded
    #     # Assume it's a single path to SonusAI mixdb subdir
    #     num_featparams = mixdb.feature_parameters
    #     logger.debug(f"SonusAI mixdb: found {mixdb.num_mixtures} mixtures with {num_featparams} classes")
    #     p_mixids = mixdb.mixids_to_list(mixids)
    #     if len(p_mixids) != mixdb.num_mixtures:
    #         logger.info(f"Processing a subset of {p_mixids} from available mixtures.")
    # else:
    # for p in data_paths:
    #     location = join(realpath(abspath(p)), "**", include)
    #     logger.debug(f"Processing files in {location}")
    #     for file in braced_iglob(pathname=location, recursive=True):
    #         name = file
    #         entries.append(PathInfo(abs_path=file, audio_filepath=name))
    # logger.info(f"{len(data_paths)} data paths specified, found {len(pfile)} audio files.")

    # feature, _ = reshape_inputs(
    #     feature=feature,
    #     batch_size=1,
    #     timesteps=timesteps,
    #     flatten=hparams["flatten"],
    #     add1ch=hparams["add1ch"],
    # )

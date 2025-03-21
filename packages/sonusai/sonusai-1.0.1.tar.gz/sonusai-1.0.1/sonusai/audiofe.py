"""sonusai audiofe

usage: audiofe [-hvdsp] [--version] [-i INPUT] [-l LENGTH] [-a ASR] [-n NOISEDB]
                        [-w WMODEL] [-o FEATURE] MODEL

options:
    -h, --help
    -v, --verbose                   Be verbose.
    -d, --debug                     Write debug data to H5 file.
    -s, --show                      Display a list of available audio inputs.
    -i INPUT, --input INPUT         Audio source from ALSA or .wav file. See -s or arecord -L. [default: default]
    -l LENGTH, --length LENGTH      Length of audio in seconds. [default: -1].
    -m MODEL, --model MODEL         SonusAI ONNX model applied to the captured audio.
    -n NOISEDB, --noiseadd NOISEDB  Amount of noise to keep in clean audio output. [default: -30]
    -p, --playback                  Enable playback of noisy audio, then the model prediction output audio
    -a ASR, --asr ASR               ASR method to use.
    -w WMODEL, --whisper WMODEL     Model used in whisper, aixplain_whisper and faster_whisper methods. [default: tiny].
    -o FEATURE, --feature-overlap   Run SonusAI model in overlap-streaming mode using FEATURE which is an 8-10 character
                                    string specifying a stride-overlap feature of the same type as the model, i.e. a
                                    model with default feature of hun00ns1 could use hun00nv80 or hun00nv128, etc.

Aaware SonusAI Audio Front End.

Capture LENGTH seconds of audio from INPUT. If LENGTH is < 0, then capture until key is pressed. If INPUT is a valid
audio file name, then use the audio data from the specified file. In this case, if LENGTH is < 0, process entire file;
otherwise, process min(length(INPUT), LENGTH) seconds of audio from INPUT. Audio is saved to
audiofe_capture_<TIMESTAMP>.wav.

If a model is specified, run prediction on audio data from this model. Then compute the inverse transform of the
prediction result and save to audiofe_predict_<TIMESTAMP>.wav.

Also, if a model is specified, save plots of the capture data (time-domain signal and feature) to
audiofe_capture_<TIMESTAMP>.png and predict data (time-domain signal and feature) to
audiofe_predict_<TIMESTAMP>.png.

If an ASR is specified, run ASR on the captured audio and print the results. In addition, if a model was also specified,
run ASR on the predict audio and print the results.  Examples: faster_whisper, google,

If the debug option is enabled, write capture audio, feature, reconstruct audio, predict, and predict audio to
audiofe_<TIMESTAMP>.h5.

"""

import numpy as np

from sonusai.mixture import AudioT


def main() -> None:
    from docopt import docopt

    from sonusai import __version__ as sai_version
    from sonusai.utils import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    verbose = args["--verbose"]
    length = float(args["--length"])
    input_name = args["--input"]
    feature_ovr = args["--feature-overlap"]
    asr_name = args["--asr"]
    whisper_name = args["--whisper"]
    debug = args["--debug"]
    show = args["--show"]
    playback = args["--playback"]
    noiseadd = args["--noiseadd"]
    model_name = args["MODEL"]

    import pyaudio

    from sonusai import create_file_handler
    from sonusai import initial_log_messages
    from sonusai import logger
    from sonusai import update_console_handler
    from sonusai.utils import create_timestamp
    from sonusai.utils import get_input_devices
    from sonusai.utils import load_ort_session

    # Setup logging file
    create_file_handler("audiofe.log")
    update_console_handler(verbose)
    initial_log_messages("audiofe")

    if show:
        logger.info("List of available audio inputs:")
        logger.info("")
        p = pyaudio.PyAudio()
        for name in get_input_devices(p):
            logger.info(f"{name}")
        logger.info("")
        p.terminate()
        # return

    ts = create_timestamp()
    capture_name = f"{ts}-noisy"
    capture_wav = capture_name + ".wav"
    capture_png = capture_name + ".png"
    predict_name = f"{ts}-pred"
    predict_wav = predict_name + ".wav"
    predict_png = predict_name + ".png"
    h5_name = f"{ts}-audiofe.h5"

    if model_name is not None:
        session, options, model_root, hparams, sess_inputs, sess_outputs = load_ort_session(model_name)
        if hparams is None:
            logger.error("Error: ONNX model does not have required SonusAI hyperparameters, cannot proceed.")
            raise SystemExit(1)
        feature_mode = hparams["feature"]
        if feature_ovr is not None:
            # TBD checks for match and valid feature_ovr
            stride = int(feature_ovr[7:])
            sov_type = feature_ovr[6]  # v,e,f,t supported, need to calculate stride from tstep
            if sov_type == "v":
                feat_step = int(np.ceil(0.5 * stride))
            elif sov_type == "e":
                feat_step = int(np.ceil(4 * stride / 5))
            elif sov_type == "f":
                feat_step = int(np.ceil(3 * stride / 4))
            elif sov_type == "t":
                feat_step = int(np.ceil(2 * stride / 3))
            else:
                logger.error("Override feature does not have a supported overlap mode, exiting.")
                raise SystemExit(1)
            feature_orig = feature_mode
            feature_mode = feature_ovr
            logger.info(
                f"Overriding feature with {feature_ovr} (was {feature_orig}), with stride={stride}, step={feat_step}."
            )
        else:
            feat_step = 1

        from pyaaware import FeatureGenerator

        fg = FeatureGenerator(feature_mode=feature_mode)
        ftn = fg.ftransform_length  # feature transform length
        ftr = fg.ftransform_overlap  # forward transform samples per step (R)
        fstride = fg.stride  # feature stride
        fsamples = fstride * ftr  # total samples in feature

        in0name = sess_inputs[0].name
        in0type = sess_inputs[0].type
        out_names = [n.name for n in session.get_outputs()]
        if len(sess_inputs) != 1:
            logger.error(f"Error: ONNX model does not have 1 input, but {len(sess_inputs)}. Exit due to unknown input.")
            raise SystemExit(1)
        if verbose:
            logger.info(f"Read and compiled ONNX model from {model_name}.")
            import onnx

            omodel = onnx.load(model_name)
            from sonusai.utils.onnx_utils import get_and_check_inputs
            from sonusai.utils.onnx_utils import get_and_check_outputs

            logger.info(f"Onnx model uses ir_version {omodel.ir_version}")
            onnx_inputs, inshapes = get_and_check_inputs(omodel)  # Note: logs warning if # inputs > 1
            logger.info(f"Onnx model input has {len(inshapes[0])} dims with shape (0 means dynamic): {inshapes[0]}")
            logger.info(f"Onnx model input has type: {in0type}")
            onnx_outputs, oshapes = get_and_check_outputs(omodel)
            logger.info(f"Onnx model output has {len(oshapes[0])} dims with shape (0 means dynamic): {oshapes[0]}")
            import onnxruntime as ort

            providers = ort.get_available_providers()
            logger.info(f"ONNX runtime available providers: {providers}.")
    else:
        logger.error("No ONNX model provided, exiting.")
        raise SystemExit(1)

    from os.path import exists

    import h5py

    from sonusai.constants import SAMPLE_RATE
    from sonusai.mixture import get_audio_from_feature
    from sonusai.mixture import get_feature_from_audio
    from sonusai.utils import calc_asr
    from sonusai.utils import write_audio

    if input_name is not None and exists(input_name):
        capture_audio = get_frames_from_file(input_name, length)
    else:
        try:
            capture_audio = get_frames_from_device(input_name, length)
        except ValueError as e:
            logger.exception(e)
            return
        # Only write if capture from device, not for file input
        write_audio(capture_wav, capture_audio, SAMPLE_RATE)
        logger.debug("")
        logger.debug(f"Wrote capture audio with shape {capture_audio.shape} to {capture_wav}")

    # Pad audio to transform step size
    padlen_tf = int(np.ceil(len(capture_audio) / ftr)) * ftr - len(capture_audio)
    capture_audio = np.pad(capture_audio, (0, padlen_tf), "constant", constant_values=(0, 0))

    if debug:
        with h5py.File(h5_name, "a") as f:
            if "capture_audio" in f:
                del f["capture_audio"]
            f.create_dataset("capture_audio", data=capture_audio)
        logger.info(f"Wrote capture feature data with shape {capture_audio.shape} to {h5_name}")

    if asr_name is not None:
        logger.info(f"Running ASR on captured audio with {asr_name} ...")
        capture_asr = calc_asr(capture_audio, engine=asr_name, model=whisper_name).text
        logger.info(f"Noisy audio ASR: {capture_asr}")

    if model_name is not None:
        # Pad audio to fill total feature stride * transform stride samples
        padlen = int(np.ceil(len(capture_audio) / fsamples)) * fsamples - len(capture_audio)
        capture_audio_p = np.pad(capture_audio, (0, padlen), "constant", constant_values=(0, 0))

        # feature always frames x stride x feat_params, convert to always Batch x Tsteps x Bins
        feature = get_feature_from_audio(audio=capture_audio_p, feature_mode=feature_mode)
        if debug:
            with h5py.File(h5_name, "a") as f:
                if "feature" in f:
                    del f["feature"]
                f.create_dataset("feature", data=feature)
            logger.info(f"Wrote feature with shape {feature.shape} to {h5_name}")

        feat_nov = sov2nov(feature, feat_step)  # remove overlap, output always Batch x Tsteps x Bins
        # TBD remove padding of feature-stride
        # if padlen > 0:
        save_figure(capture_png, capture_audio, feat_nov)
        logger.info(f"Wrote capture plots to {capture_png}")

        if feature_ovr is not None:
            test_audio = get_audio_from_feature(feature=feat_nov, feature_mode=feature_orig)
            # write_audio(f'{ts}-noisy-itf.wav', test_audio, SAMPLE_RATE)
        else:
            # feature is frames x 1 x Bins, reshape to 1 x frames x Bins for model
            feature = feature.transpose((1, 0, 2))

        if in0type.find("float16") != -1:
            logger.info("Detected input of float16, converting all feature inputs to that type.")
            feature = np.float16(feature)  # type: ignore

        # Run inference, ort session wants batch x timesteps x feat_params, outputs numpy BxTxFP or BxFP
        # Note full reshape not needed here since we assume speech enhancement type model, so a transpose suffices
        logger.info(f"Running model on data with shape {feature.shape} ...")
        if feature_ovr is None:
            predict = session.run(out_names, {in0name: feature})[0]  # standard mode (entire batch)
        else:
            predict = np.zeros(feature.shape)
            for i in range(predict.shape[0]):
                logger.debug(f"running batch: {i}")
                predict[i, :, :] = session.run(out_names, {in0name: feature[i : i + 1, :, :]})[0]

        if debug:
            with h5py.File(h5_name, "a") as f:
                if "predict" in f:
                    del f["predict"]
                f.create_dataset("predict", data=predict)
            logger.info(f"Wrote predict data with shape {predict.shape} to {h5_name}")

        if feature_ovr is not None:
            predict = sov2nov(predict, feat_step)  # always returns batch x tsteps x feat_params
            predict_audio = get_audio_from_feature(feature=predict, feature_mode=feature_orig)
        else:
            predict = predict.transpose((1, 0, 2))  # need transpose to frames x 1 x bins
            predict_audio = get_audio_from_feature(feature=predict, feature_mode=feature_mode)

        if predict_audio.shape[0] > capture_audio.shape[0]:
            predict_audio = predict_audio[0 : (capture_audio.shape[0] - predict_audio.shape[0])]

        if predict_audio.shape[0] < capture_audio.shape[0]:
            capture_audio = capture_audio[0 : (predict_audio.shape[0] - capture_audio.shape[0])]

        if noiseadd is not None:
            ngain = np.power(10, min(float(noiseadd), 0.0) / 20.0)  # limit to gain <1, convert to float
            if ngain < 1.0:  # don't apply if it's 1.0
                logger.info(f"Adding back noise with gain of {ngain} = {noiseadd} db.")
                noise = capture_audio - predict_audio
                predict_audio = predict_audio + ngain * noise

        write_audio(predict_wav, predict_audio, SAMPLE_RATE)
        logger.info(f"Wrote predict audio with shape {predict_audio.shape} to {predict_wav}")
        if debug:
            with h5py.File(h5_name, "a") as f:
                if "predict_audio" in f:
                    del f["predict_audio"]
                f.create_dataset("predict_audio", data=predict_audio)
            logger.info(f"Wrote predict audio with shape {predict_audio.shape} to {h5_name}")

        save_figure(predict_png, predict_audio, predict)
        logger.info(f"Wrote predict plots to {predict_png}")

        if asr_name is not None:
            logger.info(f"Running ASR on model-enhanced audio with {asr_name} ...")
            predict_asr = calc_asr(predict_audio, engine=asr_name, model=whisper_name).text
            logger.info(f"Predict audio ASR: {predict_asr}")

        plot_en = True
        if plot_en is not None:
            import subprocess

            # Construct plot command using spgramd, start the process non-blocking (will leave matplot open)
            command = ["python", "spgramd.py", capture_wav, predict_wav]
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if playback is not None:
            import sh

            sh.play(capture_wav)
            sh.play(predict_wav)
            flag_end = False
            while not flag_end:
                choice = input("Press 'r' to replay or 'q' to quit: ").strip().lower()
                if choice == "q":
                    print("Quitting...")
                    flag_end = True
                elif choice == "r":
                    print("Replaying...")
                    sh.play(capture_wav)
                    sh.play(predict_wav)
                else:
                    print("Invalid input. Please try again.")


def get_frames_from_device(input_name: str | None, length: float, chunk: int = 1024) -> AudioT:
    from select import select
    from sys import stdin

    import pyaudio

    from sonusai import logger
    from sonusai.constants import CHANNEL_COUNT
    from sonusai.constants import SAMPLE_RATE
    from sonusai.utils import get_input_device_index_by_name
    from sonusai.utils import get_input_devices

    p = pyaudio.PyAudio()

    input_devices = get_input_devices(p)
    if not input_devices:
        raise ValueError("No input audio devices found")

    if input_name is None:
        input_name = input_devices[0]

    try:
        device_index = get_input_device_index_by_name(p, input_name)
    except ValueError as ex:
        msg = f"Could not find {input_name}\n"
        msg += "Available devices:\n"
        for input_device in input_devices:
            msg += f"  {input_device}\n"
        raise ValueError(msg) from ex

    logger.info(f"Capturing from {p.get_device_info_by_index(device_index).get('name')}")
    stream = p.open(
        format=pyaudio.paFloat32, channels=CHANNEL_COUNT, rate=SAMPLE_RATE, input=True, input_device_index=device_index
    )
    stream.start_stream()

    print()
    print("+---------------------------------+")
    print("| Press Enter to stop             |")
    print("+---------------------------------+")
    print()

    elapsed = 0.0
    seconds_per_chunk = float(chunk) / float(SAMPLE_RATE)
    raw_frames = []
    while elapsed < length or length == -1:
        raw_frames.append(stream.read(num_frames=chunk, exception_on_overflow=False))
        elapsed += seconds_per_chunk
        if select(
            [
                stdin,
            ],
            [],
            [],
            0,
        )[0]:
            stdin.read(1)
            length = elapsed

    stream.stop_stream()
    stream.close()
    p.terminate()
    frames = np.frombuffer(b"".join(raw_frames), dtype=np.float32)
    return frames


def get_frames_from_file(input_name: str, length: float) -> AudioT:
    from sonusai import logger
    from sonusai.constants import SAMPLE_RATE
    from sonusai.mixture import read_audio

    logger.info(f"Capturing from {input_name}")
    frames = read_audio(input_name)
    if length != -1:
        num_frames = int(length * SAMPLE_RATE)
        if len(frames) > num_frames:
            frames = frames[:num_frames]
    return frames


def sov2nov(feature: np.ndarray, step: int) -> np.ndarray:
    """Convert stride-overlap batch x stride x bins to no overlap frames x 1 x bins"""

    stride = feature.shape[1]  # stride, tsteps is set to stride in sov mode
    if stride == 1:
        return feature  # no reshape if stride is already 1
    # else:
    #     hs = feature.shape[1]//2   # half of stride
    #     nb = feature.shape[0]      # batches

    nb = feature.shape[0]
    fout = feature[:, (stride - step) :, :]  # take last
    fout = np.reshape(fout, [step * nb, 1, feature.shape[2]])
    return fout  # np.transpose(fout,[1,0,2])


def save_figure(name: str, audio: np.ndarray, feature: np.ndarray) -> None:
    import matplotlib.pyplot as plt
    from scipy.interpolate import CubicSpline

    from sonusai.constants import SAMPLE_RATE
    from sonusai.utils import unstack_complex

    spectrum = 20 * np.log(np.abs(np.squeeze(unstack_complex(feature)).transpose()) + 1e-7)
    frames = spectrum.shape[1]
    samples = (len(audio) // frames) * frames
    length_in_s = samples / SAMPLE_RATE
    interp = samples // frames

    ts = np.arange(0.0, length_in_s, interp / SAMPLE_RATE)
    t = np.arange(0.0, length_in_s, 1 / SAMPLE_RATE)

    spectrum = CubicSpline(ts, spectrum, axis=-1)(t)

    fig, (ax1, ax2) = plt.subplots(nrows=2)
    ax1.set_title(name)
    ax1.plot(t, audio[:samples])
    ax1.set_ylabel("Signal")
    ax1.set_xlim(0, length_in_s)
    ax1.set_ylim(-1, 1)

    ax2.imshow(spectrum, origin="lower", aspect="auto")
    ax2.set_xticks([])
    ax2.set_ylabel("Feature")

    plt.savefig(name, dpi=300)


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)


# import subprocess
#
# # Define the arguments
# arg1 = "value1"
# arg2 = "value2"
#
# # Construct the command
# command = ["python", "script.py", arg1, arg2]
#
# # Start the process
# process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#
# # Optionally, you can communicate with the process later if needed
# # For example, to wait for the process to finish and get the output
# stdout, stderr = process.communicate()
#
# # Check if the process was successful
# if process.returncode == 0:
#     print("Process executed successfully:")
#     print(stdout)
# else:
#     print("Process failed:")
#     print(stderr)

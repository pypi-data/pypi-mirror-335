"""sonusai ir_metric

usage: ir_metric [-h] [-n NCPU] IRLOC

options:
    -h, --help
    -n, --num_process NCPU      Number of parallel processes to use [default: auto]

Calculate delay and gain metrics of impulse response (IR) files <filename>.wav in IRLOC.
Metrics include gain and multiple ways to calculate the IR delay:
 - gmax:  max abs(fft(ir,4096))
 - dcc:   cross-correlation of ir with pulse train
 - dmax:  index of max(ir)
 - dgd:   group delay method
 - dcen:  centroid of energy

Results are written into IRLOC/ir_metrics.txt

IRLOC  directory containing impulse response data in audio files (.wav, .flac, etc.). Only first channel is analyzed.

"""

import glob
from os.path import abspath
from os.path import basename
from os.path import commonprefix
from os.path import dirname
from os.path import isdir
from os.path import isfile
from os.path import join
from os.path import relpath
from os.path import splitext

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import soundfile
from numpy import fft

from sonusai.utils import braced_iglob


def tdoa(signal, reference, interp=1, phat=False, fs=1, t_max=None):
    """
    Estimates the shift of array signal with respect to reference
    using generalized cross-correlation

    Parameters
    ----------
    signal: array_like
        The array whose tdoa is measured
    reference: array_like
        The reference array
    interp: int, optional
        The interpolation factor for the output array, default 1.
    phat: bool, optional
        Apply the PHAT weighting (default False)
    fs: int or float, optional
        The sampling frequency of the input arrays, default=1

    Returns
    -------
    The estimated delay between the two arrays
    """

    signal = np.array(signal)
    reference = np.array(reference)

    N1 = signal.shape[0]
    N2 = reference.shape[0]

    r_12 = correlate(signal, reference, interp=interp, phat=phat)

    delay = (np.argmax(np.abs(r_12)) / interp - (N2 - 1)) / fs

    return delay


def correlate(x1, x2, interp=1, phat=False):
    """
    Compute the cross-correlation between x1 and x2

    Parameters
    ----------
    x1,x2: array_like
        The data arrays
    interp: int, optional
        The interpolation factor for the output array, default 1.
    phat: bool, optional
        Apply the PHAT weighting (default False)

    Returns
    -------
    The cross-correlation between the two arrays
    """

    N1 = x1.shape[0]
    N2 = x2.shape[0]

    N = N1 + N2 - 1

    X1 = fft.rfft(x1, n=N)
    X2 = fft.rfft(x2, n=N)

    if phat:
        eps1 = np.mean(np.abs(X1)) * 1e-10
        X1 /= np.abs(X1) + eps1
        eps2 = np.mean(np.abs(X2)) * 1e-10
        X2 /= np.abs(X2) + eps2

    m = np.minimum(N1, N2)

    out = fft.irfft(X1 * np.conj(X2), n=int(N * interp))

    return np.concatenate([out[-interp * (N2 - 1) :], out[: (interp * N1)]])


def hilbert(u):
    # N : fft length
    # M : number of elements to zero out
    # U : DFT of u
    # v : IDFT of H(U)

    N = len(u)
    # take forward Fourier transform
    U = fft.fft(u)
    M = N - N // 2 - 1
    # zero out negative frequency components
    U[N // 2 + 1 :] = [0] * M
    # double fft energy except @ DC0
    U[1 : N // 2] = 2 * U[1 : N // 2]
    # take inverse Fourier transform
    v = fft.ifft(U)
    return v


def measure_rt60(h, fs=1, decay_db=60, energy_thres=1.0, plot=False, rt60_tgt=None):
    """
    RT60 Measurement Routine (taken/modified from Pyroom acoustics.)

    Calculates reverberation time of an impulse response using the Schroeder method [1].
    Returns:
    rt60:  Reverberation time to -60db  (-5db to -65db), will be estimated from rt20 or rt10 if noise floor > -65db
    edt:   Early decay time from 0db to -10db
    rt10:  Reverberation time to -10db (-5db to -15db)
    rt20:  Reverberation time to -20db (-5db to -25db), will be estimated from rt10 if noise floor > -25db
    floor: 0 if noise floor > -10db or energy curve is not a decay
           1 if noise floor > -15db and edt is measured, but rt10 estimated from entire energy curve length
           2 if noise -15db > floor > -25db, rt20 is estimated from measured rt10
           3 if noise -25db > floor > -65db, rt60 is estimated from measured rt20
           4 if noise floor < -65db, rt60, edt, rt10, rt20 are all measured
    Optionally plots some useful information.

    Parameters
    ----------
    h: array_like
        The impulse response.
    fs: float or int, optional
        The sampling frequency of h (default to 1, i.e., samples).
    decay_db: float or int, optional
        The decay in decibels for which we actually estimate the slope and time.
        Although we want to estimate the RT60, it might not be practical. Instead,
        we measure the RT10, RT20 or RT30 and extrapolate to RT60.
    energy_thres: float
        This should be a value between 0.0 and 1.0.
        If provided, the fit will be done using a fraction energy_thres of the
        whole energy. This is useful when there is a long noisy tail for example.
    plot: bool, optional
        If set to ``True``, the power decay and different estimated values will
        be plotted (default False).
    rt60_tgt: float
        This parameter can be used to indicate a target RT60 to which we want
        to compare the estimated value.

    References
    ----------

    [1] M. R. Schroeder, "New Method of Measuring Reverberation Time,"
        J. Acoust. Soc. Am., vol. 37, no. 3, pp. 409-412, Mar. 1968.
    """

    h = np.array(h)
    fs = float(fs)
    h = np.abs(hilbert(h))  # hilbert from scratch, see above

    # The power of the impulse response in dB
    power = h**2
    # Backward energy integration according to Schroeder
    energy = np.cumsum(power[::-1])[::-1]  # Integration according to Schroeder

    if energy_thres < 1.0:
        assert 0.0 < energy_thres < 1.0
        energy -= energy[0] * (1.0 - energy_thres)
        energy = np.maximum(energy, 0.0)

    # remove the possibly all zero tail
    i_nz = np.max(np.where(energy > 0)[0])
    energy = energy[:i_nz]
    energy_db = 10 * np.log10(energy)
    energy_db -= energy_db[0]  # normalize to first sample assuming it's the peak

    min_energy_db = -np.min(energy_db)
    if min_energy_db - 5 < decay_db:
        decay_db = min_energy_db

    # -5 dB headroom
    try:
        i_5db = np.min(np.where(energy_db < -5)[0])
    except ValueError:
        floor = 0
        return 0.0, 0.0, 0.0, 0.0, floor  # failed, energy curve is not a decay, or has noise floor tail above -5db
    e_5db = energy_db[i_5db]
    t_5db = i_5db / fs  # This is the initial decay to -5db, used as start of decay slope measurements

    # Estimate slope from 0db to -10db - this is also known as EDT (early decay time)
    try:
        i_10db = np.min(np.where(energy_db < -10)[0])
    except ValueError:
        floor = 0
        return 0.0, 0.0, 0.0, 0.0, floor  # failed, energy curve is not a decay, or noise floor tail above -10db
    e_10db = energy_db[i_10db]
    edt = i_10db / fs  # this is also known as EDT (early decay time)

    # after initial decay, estimate RT10, RT20, RT60
    try:
        i_decay10db = np.min(np.where(energy_db < -5 - 10)[0])
    except ValueError:
        floor = 1
        i_decay10db = len(energy_db)  # noise floor tail is above -15db, use entire curve
    t10_decay = i_decay10db / fs
    rt10 = t10_decay - t_5db

    try:
        i_decay20db = np.min(np.where(energy_db < -5 - 20)[0])
    except ValueError:
        floor = 2
        i_decay20db = len(energy_db)  # noise floor tail is above -20db, use entire curve
    t20_decay = i_decay20db / fs
    rt20 = t20_decay - t_5db

    try:
        i_decay60db = np.min(np.where(energy_db < -5 - 60)[0])
        t60_decay = i_decay60db / fs
        rt60 = t60_decay - t_5db
        floor = 4
    except ValueError:
        floor = 3
        i_decay60db = len(energy_db)  # noise floor tail is above -60db, use t20_decay to estimate
        t60_decay = 3 * i_decay20db / fs
        rt60 = t60_decay - t_5db

    # # extrapolate to compute the rt60 decay time from decay_db decay time
    # decay_time = t_decay - t_5db
    # est_rt60 = (60 / decay_db) * decay_time

    if plot:
        # Remove clip power below to minimum energy (for plotting purpose mostly)
        energy_min = energy[-1]
        energy_db_min = energy_db[-1]
        power[power < energy[-1]] = energy_min
        power_db = 10 * np.log10(power)
        power_db -= np.max(power_db)

        # time vector
        def get_time(x, fs):
            return np.arange(x.shape[0]) / fs - i_5db / fs

        T = get_time(power_db, fs)

        # plot power and energy
        plt.plot(get_time(energy_db, fs), energy_db, label="Energy")

        # now the linear fit
        plt.plot([0, rt60], [e_5db, -65], "--", label="Linear Fit")
        plt.plot(T, np.ones_like(T) * -60, "--", label="-60 dB")
        plt.vlines(rt60, energy_db_min, 0, linestyles="dashed", label="Estimated RT60")

        if rt60_tgt is not None:
            plt.vlines(rt60_tgt, energy_db_min, 0, label="Target RT60")

        plt.legend()

    return rt60, edt, rt10, rt20, floor


def process_path(path: str, extensions: list[str] | None = None) -> tuple[list, str | None]:
    """
    Check path which can be a single file, a subdirectory, or a regex
    return:
      - a list of files with matching extensions to any in extlist provided (i.e. ['.wav', '.mp3', '.acc'])
      - the basedir of the path, if
    """
    if extensions is None:
        extensions = [".wav", ".WAV", ".flac", ".FLAC", ".mp3", ".aac"]

    # Check if the path is a single file, and return it as a list with the dirname
    if isfile(path):
        if any(path.endswith(ext) for ext in extensions):
            basedir = dirname(path)  # base directory
            if not basedir:
                basedir = "./"
            return [path], basedir

        return [], None

    # Check if the path is a dir, recursively find all files any of the specified extensions, return file list and dir
    if isdir(path):
        matching_files = []
        for ext in extensions:
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

    return [], None


def _process_ir(pfile: str, irtab_col: list, basedir: str) -> pd.DataFrame:
    # 1)  Read ir audio file, and calc basic stats
    ir_fname = pfile[1]  # abs_path
    irwav, sample_rate = soundfile.read(ir_fname)
    if irwav.ndim == 2:
        irwav = irwav[:, 0]  # Only first channel of multi-channel
    duration = len(irwav) / sample_rate
    srk = sample_rate / 1000
    ir_basename = relpath(ir_fname, basedir)

    # 2) Compute delay via autocorrelation (not working - always zero, use interplated tdoa instead)
    # ar = np.correlate(irwav, irwav, mode='same')
    # acdelay_index = np.argmax(ar)
    # dacc= acdelay_index - len(ar) // 2  # Center the delay around 0 of 'same' mode

    # 3) Compute delay via max argument - find the peak
    peak_index = np.argmax(irwav)
    peak_value = irwav[peak_index]
    dmax = peak_index

    # 4) Calculate cross-correlation with white gaussian noise ref (ssame as pyrooma.tdoa() with interp=1)
    np.random.seed(42)
    wgn_ref = np.random.normal(0, 0.2, int(np.ceil(0.05 * sample_rate)))  # (mean,std_dev,length)
    wgn_conv = np.convolve(irwav, wgn_ref)
    wgn_corr = np.correlate(wgn_conv, wgn_ref, mode="full")  # Compute cross-correlation
    delay_index = np.argmax(np.abs(wgn_corr))  # Find the delay (need abs??, yes)
    dcc = delay_index - len(wgn_ref) + 1  # Adjust for the mode='full' shift
    # GCC with PHAT weighting known to be best, but does seem to mismatch dcc, dmax more frequently
    dtdoa = tdoa(wgn_conv, wgn_ref, interp=16, phat=True)
    gdccmax = np.max(np.abs(wgn_conv)) / np.max(np.abs(wgn_ref))  # gain of max value

    # # 4b) Calculate cross-correlation with chirp 20Hz-20KHz
    # t_end = 2  # 1s
    # t = np.linspace(0, t_end, int(t_end * sample_rate))
    # k = (20 - 20000) / t_end
    # chrp_phase = 2 * np.pi * (20 * t + 0.5 * k * t ** 2)
    # chrp = np.cos(chrp_phase)
    # chrp_convout = np.convolve(irwav,chrp)
    # chrp_corr = np.correlate(chrp_convout, chrp, mode='full')     # Compute cross-correlation
    # chrp_delay_idx = np.argmax(np.abs(chrp_corr))
    # dcchr = chrp_delay_idx - len(chrp) + 1
    # dtdoachr = tdoa(chrp_convout, chrp, interp=16, phat=False)
    # gdcchrmax = np.max(np.abs(chrp_convout)) / np.max(np.abs(chrp))
    # #sin_ref = np.sin(2 * np.pi * 500/sample_rate * np.arange(0,sample_rate))

    # # Create a pulse train alternating +1, -1, ... of width PW, spacing PS_ms
    # PS = int(0.010 * sample_rate)     # Spacing between pulses in sec (to samples)
    # PW = 5                          # Pulse width in samples, make sure < PS
    # PTLEN = int(1 * sample_rate)      # Length in sec (to samples)
    # #sample_vec = np.arange(PTLEN)
    #
    # # Construct the pulse train
    # ptrain_ref = np.zeros(PTLEN)
    # polarity = 1
    # for i in range(0, PTLEN, PS):
    #     if polarity == 1:
    #         ptrain_ref[i:(i + PW)] = 1
    #         polarity = -1
    #     else:
    #         ptrain_ref[i:(i + PW)] = -1
    #         polarity = 1
    #
    # pt_convout = np.convolve(irwav,ptrain_ref)
    # pt_corr = np.correlate(pt_convout, ptrain_ref, mode='full')     # Compute cross-correlation
    # pt_delay_idx = np.argmax(np.abs(pt_corr))
    # dcc = pt_delay_idx - len(ptrain_ref) + 1
    # dtdoa = tdoa(pt_convout, ptrain_ref, interp=16, phat=True)
    # gdccptmax = np.max(np.abs(pt_convout)) / np.max(np.abs(ptrain_ref))

    # 5) Calculate delay using group_delay method
    fft_size = len(irwav)
    H = np.fft.fft(irwav, n=fft_size)
    phase = np.unwrap(np.angle(H))
    freq = np.fft.fftfreq(fft_size)  # in samples, using d=1/sampling_rate=1
    group_delay = -np.gradient(phase) / (2 * np.pi * np.gradient(freq))
    dagd = np.mean(group_delay[np.isfinite(group_delay)])  # Average group delay
    gmax = max(np.abs(H))

    rt60, edt, rt10, rt20, nfloor = measure_rt60(irwav, sample_rate, plot=False)

    # 4) Tabulate metrics as single row in table of scalar metrics per mixture
    # irtab_col = ["dmax", "dcc", "dccphat", "dagd", "gdccmax", "rt20", "rt60", "max", "min", "gmax", "dur", "sr", "irfile"]
    metr1 = [dmax, dcc, dtdoa, dagd, gdccmax, rt20, rt60, peak_value, min(irwav), gmax, duration, srk, ir_basename]
    mtab1 = pd.DataFrame([metr1], columns=irtab_col, index=[pfile[0]])  # return tuple of dataframe

    return mtab1


def main():
    from docopt import docopt

    from . import __version__ as sai_version
    from .utils.docstring import trim_docstring

    args = docopt(trim_docstring(__doc__), version=sai_version, options_first=True)

    ir_location = args["IRLOC"]
    num_proc = args["--num_process"]

    import psutil

    from .utils.create_timestamp import create_timestamp
    from .utils.parallel import par_track
    from .utils.parallel import track

    # Check location, default ext are ['.wav', '.WAV', '.flac', '.FLAC', '.mp3', '.aac']
    pfiles, basedir = process_path(ir_location)
    pfiles = sorted(pfiles, key=basename)

    if pfiles is None or len(pfiles) < 1:
        print(f"No IR audio files found in {ir_location}, exiting ...")
        raise SystemExit(1)
    if len(pfiles) == 1:
        print(f"Found single IR audio file {ir_location} , writing to *-irmetric.txt ...")
        fbase, ext = splitext(basename(pfiles[0]))
        wlcsv_name = None
        txt_fname = str(join(basedir, fbase + "-irmetric.txt"))
    else:
        print(f"Found {len(pfiles)} files under {basedir} for impulse response metric calculations")
        wlcsv_name = str(join(basedir, "ir_metric_list.csv"))
        txt_fname = str(join(basedir, "ir_metric_summary.txt"))

    num_cpu = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"#CPUs: {num_cpu}, current CPU utilization: {cpu_percent}%")
    print(f"Memory utilization: {psutil.virtual_memory().percent}%")
    if num_proc == "auto":
        use_cpu = int(num_cpu * (0.9 - cpu_percent / 100))  # default use 80% of available cpus
    elif num_proc == "None":
        use_cpu = None
    else:
        use_cpu = min(max(int(num_proc), 1), num_cpu)

    timestamp = create_timestamp()
    # Individual mixtures use pandas print, set precision to 2 decimal places
    # pd.set_option('float_format', '{:.2f}'.format)
    print(f"Calculating metrics for {len(pfiles)} impulse response files using {use_cpu} parallel processes ...")
    progress = track(total=len(pfiles))
    if use_cpu is None or len(pfiles) == 1:
        no_par = True
        num_cpus = None
    else:
        no_par = False
        num_cpus = use_cpu

    from functools import partial

    # Setup pandas table for summarizing ir metrics
    irtab_col = [
        "dmax",
        "dcc",
        "dccphat",
        "dagd",
        "gdccmax",
        "rt20",
        "rt60",
        "max",
        "min",
        "gmax",
        "dur",
        "sr",
        "irfile",
    ]
    idx = range(len(pfiles))
    llfiles = list(zip(idx, pfiles, strict=False))

    all_metrics_tables = par_track(
        partial(
            _process_ir,
            irtab_col=irtab_col,
            basedir=basedir,
        ),
        llfiles,
        progress=progress,
        num_cpus=num_cpus,
        no_par=no_par,
    )
    progress.close()

    # progress = tqdm(total=len(pfiles), desc='ir_metric')
    # if use_cpu is None:
    #     all_metrics_tab = pp_tqdm_imap(_process_mixture, pfiles, progress=progress, no_par=True)
    # else:
    #     all_metrics_tab = pp_tqdm_imap(_process_mixture, pfiles, progress=progress, num_cpus=use_cpu)
    # progress.close()

    header_args = {
        "mode": "a",
        "encoding": "utf-8",
        "index": False,
        "header": False,
    }
    table_args = {
        "mode": "a",
        "encoding": "utf-8",
    }

    all_metrics_tab = pd.concat([item for item in all_metrics_tables])  # already sorted by truth filename via idx
    mtabsort = all_metrics_tab.sort_values(by=["irfile"])

    # Write list to .csv
    if wlcsv_name:
        pd.DataFrame([["Timestamp", timestamp]]).to_csv(wlcsv_name, header=False, index=False)
        pd.DataFrame([f"IR metric list for {ir_location}:"]).to_csv(wlcsv_name, mode="a", header=False, index=False)
        mtabsort.round(2).to_csv(wlcsv_name, **table_args)

    # Write summary and list to .txt
    with open(txt_fname, "w") as f:
        print(f"Timestamp: {timestamp}", file=f)
        print(f"IR metrics stats over {len(llfiles)} files:", file=f)
        print(mtabsort.describe().round(3).T.to_string(float_format=lambda x: f"{x:.3f}", index=True), file=f)
        print("", file=f)
        print("", file=f)
        print([f"IR metric list for {ir_location}:"], file=f)
        print(mtabsort.round(3).to_string(), file=f)


if __name__ == "__main__":
    from sonusai import exception_handler
    from sonusai.utils import register_keyboard_interrupt

    register_keyboard_interrupt()
    try:
        main()
    except Exception as e:
        exception_handler(e)

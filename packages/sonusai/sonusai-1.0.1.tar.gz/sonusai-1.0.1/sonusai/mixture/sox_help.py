def allpass() -> str:
    return """
allpass frequency[k] width[h|k|o|q]
    Apply a two-pole all-pass filter with central frequency (in Hz) frequency,
    and filter-width width. An all-pass filter changes the audio's frequency to
    phase relationship without changing its frequency to amplitude relationship.
"""


def band() -> str:
    return """
band [-n] center[k] [width[h|k|o|q]]
    Apply a band-pass filter. The frequency response drops logarithmically around
    the center frequency. The width parameter gives the slope of the drop. The
    frequencies at center + width and center - width will be half of their original
    amplitudes. band defaults to a mode oriented to pitched audio, i.e. voice,
    singing, or instrumental music. The -n (for noise) option uses the alternate
    mode for un-pitched audio (e.g. percussion). Warning: -n introduces a power-gain
    of about 11 dB in the filter, so beware of output clipping. band introduces noise
    in the shape of the filter, i.e. peaking at the center frequency and settling
    around it.

    See also sinc for a bandpass filter with steeper shoulders.
"""


def bandpass() -> str:
    return """
bandpass [-c] frequency[k] width[h|k|o|q]
    Apply a two-pole Butterworth band-pass filter with central frequency frequency,
    and (3 dB-point) band-width width. The -c option applies only to bandpass and
    selects a constant skirt gain (peak gain = Q) instead of the default: constant
    0 dB peak gain. The filters roll off at 6 dB per octave (20 dB per decade).

    See also sinc for a bandpass filter with steeper shoulders.
"""


def bandreject() -> str:
    return """
bandreject [-c] frequency[k] width[h|k|o|q]
    Apply a two-pole Butterworth band-reject filter with central frequency frequency,
    and (3 dB-point) band-width width. The -c option applies only to bandpass and
    selects a constant skirt gain (peak gain = Q) instead of the default: constant
    0 dB peak gain. The filters roll off at 6 dB per octave (20 dB per decade).

    See also sinc for a bandpass filter with steeper shoulders.
"""


def bass() -> str:
    return """
bass gain [frequency[k] [width[s|h|k|o|q]]]
    Boost or cut the bass (lower) frequencies of the audio using a two-pole shelving
    filter with a response similar to that of a standard hi-fi's tone-controls. This
    is also known as shelving equalisation (EQ).

    gain gives the gain at 0 Hz. Its useful range is about -20 (for a large cut) to
    +20 (for a large boost). Beware of Clipping when using a positive gain.

    If desired, the filter can be fine-tuned using the following optional parameters:

    frequency sets the filter's central frequency and so can be used to extend or reduce
    the frequency range to be boosted or cut. The default value is 100 Hz.

    width determines how steep is the filter's shelf transition. In addition to the
    common width specification methods described above, 'slope' (the default, or if
    appended with 's') may be used. The useful range of 'slope' is about 0.3, for a
    gentle slope, to 1 (the maximum), for a steep slope; the default value is 0.5.

    See also equalizer for a peaking equalisation effect.
"""


def biquad() -> str:
    return """
biquad b0 b1 b2 a0 a1 a2
    Apply a biquad IIR filter with the given coefficients. Where b* and a* are the numerator
    and denominator coefficients respectively.

    See https://en.wikipedia.org/wiki/Digital_biquad_filter (where a0 = 1).
"""


def chorus() -> str:
    return """
chorus gain-in gain-out <delay decay speed depth -s|-t>
    Add a chorus effect to the audio. This can make a single vocal sound like a chorus,
    but can also be applied to instrumentation.

    Chorus resembles an echo effect with a short delay, but whereas with echo the delay
    is constant, with chorus, it is varied using sinusoidal or triangular modulation. The
    modulation depth defines the range the modulated delay is played before or after the
    delay. Hence the delayed sound will sound slower or faster, that is the delayed sound
    tuned around the original one, like in a chorus where some vocals are slightly off key.

    Each four-tuple parameter delay/decay/speed/depth gives the delay in milliseconds and
    the decay (relative to gain-in) with a modulation speed in Hz using depth in
    milliseconds. The modulation is either sinusoidal (-s) or triangular (-t). Gain-out is
    the volume of the output.

    A typical delay is around 40 ms to 60 ms; the modulation speed is best near 0.25 Hz and
    the modulation depth around 2 ms. For example, a single delay:

    play guitar1.wav chorus 0.7 0.9 55 0.4 0.25 2 -t

    Two delays of the original samples:

    play guitar1.wav chorus 0.6 0.9 50 0.4 0.25 2 -t 60 0.32 0.4 1.3 -s

    A fuller sounding chorus (with three additional delays):

    play guitar1.wav chorus 0.5 0.9 50 0.4 0.25 2 -t 60 0.32 0.4 2.3 -t 40 0.3 0.3 1.3 -s
"""


def compand() -> str:
    return """
compand attack1,decay1{,attack2,decay2} [soft-knee-dB:]in-dB1[,out-dB1]{,in-dB2,out-dB2} [gain [initial-volume-dB [delay]]]
    Compand (compress or expand) the dynamic range of the audio.

    The attack and decay parameters (in seconds) determine the time over which the
    instantaneous level of the input signal is averaged to determine its volume; attacks
    refer to increases in volume and decays refer to decreases. For most situations, the
    attack time (response to the music getting louder) should be shorter than the decay
    time because the human ear is more sensitive to sudden loud music than sudden soft
    music. Where more than one pair of attack/decay parameters are specified, each input
    channel is companded separately and the number of pairs must agree with the number of
    input channels. Typical values are 0.3,0.8 seconds.

    The second parameter is a list of points on the compander's transfer function specified
    in dB relative to the maximum possible signal amplitude. The input values must be in a
    strictly increasing order but the transfer function does not have to be monotonically
    rising. If omitted, the value of out-dB1 defaults to the same value as in-dB1; levels
    below in-dB1 are not companded (but may have gain applied to them). The point 0,0 is
    assumed but may be overridden (by 0,out-dBn). If the list is preceded by a soft-knee-dB
    value, then the points at where adjacent line segments on the transfer function meet
    will be rounded by the amount given. Typical values for the transfer function are
    6:-70,-60,-20.

    The third (optional) parameter is an additional gain in dB to be applied at all points on
    the transfer function and allows easy adjustment of the overall gain.

    The fourth (optional) parameter is an initial level to be assumed for each channel when
    companding starts. This permits the user to supply a nominal level initially, so that,
    for example, a very large gain is not applied to initial signal levels before the
    companding action has begun to operate: it is quite probable that in such an event,
    the output would be severely clipped while the compander gain properly adjusts itself.
    A typical value (for audio which is initially quiet) is -90 dB.

    The fifth (optional) parameter is a delay in seconds. The input signal is analysed
    immediately to control the compander, but it is delayed before being fed to the volume
    adjuster. Specifying a delay approximately equal to the attack/decay times allows the
    compander to effectively operate in a 'predictive' rather than a reactive mode. A
    typical value is 0.2 seconds.

    The following example might be used to make a piece of music with both quiet and loud
    passages suitable for listening to in a noisy environment such as a moving vehicle:

    sox asz.wav asz-car.wav compand 0.3,1 6:-70,-60,-20 -5 -90 0.2

    The transfer function ('6:-70,...') says that very soft sounds (below -70 dB) will
    remain unchanged. This will stop the compander from boosting the volume on 'silent'
    passages such as between movements. However, sounds in the range -60 dB to 0 dB (maximum
    volume) will be boosted so that the 60 dB dynamic range of the original music will be
    compressed 3-to-1 into a 20 dB range, which is wide enough to enjoy the music but narrow
    enough to get around the road noise. The '6:' selects 6 dB soft-knee companding. The
    -5 (dB) output gain is needed to avoid clipping (the number is inexact, and was derived
    by experimentation). The -90 (dB) for the initial volume will work fine for a clip that
    starts with near silence, and the delay of 0.2 (seconds) has the effect of causing the
    compander to react a bit more quickly to sudden volume changes.

    In the next example, compand is being used as a noise-gate for when the noise is at a
    lower level than the signal:

    play infile compand .1,.2 -inf,-50.1,-inf,-50,-50 0 -90 .1

    Here is another noise-gate, this time for when the noise is at a higher level than the
    signal (making it, in some ways, similar to squelch):

    play infile compand .1,.1 -45.1,-45,-inf,0,-inf 45 -90 .1

    See also mcompand for a multiple-band companding effect.
"""


def contrast() -> str:
    return """
contrast [enhancement-amount(75)]
    Comparable with compression, this effect modifies an audio signal to make it sound louder.
    enhancement-amount controls the amount of the enhancement and is a number in the range 0-100.
    Note that enhancement-amount = 0 still gives a significant contrast enhancement.

    See also the compand and mcompand effects.
"""


def dcshift() -> str:
    return """
dcshift shift [limitergain]
    Apply a DC shift to the audio. This can be useful to remove a DC offset (caused perhaps by
    a hardware problem in the recording chain) from the audio. The effect of a DC offset is
    reduced headroom and hence volume. The stat or stats effect can be used to determine if a
    signal has a DC offset.

    The given dcshift value is a floating point number in the range of +/-2 that indicates the
    amount to shift the audio (which is in the range of +/-1).

    An optional limitergain can be specified as well. It should have a value much less than 1
    (e.g. 0.05 or 0.02) and is used only on peaks to prevent clipping.

    An alternative approach to removing a DC offset (albeit with a short delay) is to use the
    highpass filter effect at a frequency of say 10 Hz, as illustrated in the following example:

    sox -n dc.wav synth 5 sin %0 50
    sox dc.wav fixed.wav highpass 10
"""


def equalizer() -> str:
    return """
equalizer frequency[k] width[q|o|h|k] gain
    Apply a two-pole peaking equalisation (EQ) filter. With this filter, the signal-level at and
    around a selected frequency can be increased or decreased, whilst (unlike band-pass and
    band-reject filters) that at all other frequencies is unchanged.

    frequency gives the filter's central frequency in Hz, width, the band-width, and gain the
    required gain or attenuation in dB. Beware of Clipping when using a positive gain.

    In order to produce complex equalisation curves, this effect can be given several times, each
    with a different central frequency.

    See also bass and treble for shelving equalisation effects.
"""


def flanger() -> str:
    return """
flanger [delay depth regen width speed shape phase interp]
    Apply a flanging effect to the audio.

    All parameters are optional (right to left).
"""


def gain() -> str:
    return """
gain [-e|-B|-b|-r] [-n] [-l|-h] [gain-dB]
    Apply amplification or attenuation to the audio signal, or, in some cases, to some of its
    channels. Note that use of any of -e, -B, -b, -r, or -n requires temporary file space to store
    the audio to be processed, so may be unsuitable for use with 'streamed' audio.

    Without other options, gain-dB is used to adjust the signal power level by the given number of
    dB: positive amplifies (beware of Clipping), negative attenuates. With other options, the
    gain-dB amplification or attenuation is (logically) applied after the processing due to those
    options.

    Given the -e option, the levels of the audio channels of a multi-channel file are 'equalised',
    i.e. gain is applied to all channels other than that with the highest peak level, such that all
    channels attain the same peak level (but, without also giving -n, the audio is not 'normalised').

    The -B (balance) option is similar to -e, but with -B, the RMS level is used instead of the peak
    level. -B might be used to correct stereo imbalance caused by an imperfect record turntable
    cartridge. Note that unlike -e, -B might cause some clipping.

    -b is similar to -B but has clipping protection, i.e. if necessary to prevent clipping whilst
    balancing, attenuation is applied to all channels. Note, however, that in conjunction with
    -n, -B and -b are synonymous.

    The -r option is used in conjunction with a prior invocation of gain with the -h option - see below
    for details.

    The -n option normalises the audio to 0 dB FSD; it is often used in conjunction with a negative
    gain-dB to the effect that the audio is normalised to a given level below 0 dB. For example,

    sox infile outfile gain -n

    normalises to 0 dB, and

    sox infile outfile gain -n -3

    normalises to -3 dB.

    The -l option invokes a simple limiter, e.g.

    sox infile outfile gain -l 6

    will apply 6 dB of gain but never clip. Note that limiting more than a few dBs more than
    occasionally (in a piece of audio) is not recommended as it can cause audible distortion. See
    the compand effect for a more capable limiter.

    The -h option is used to apply gain to provide head-room for subsequent processing.
    For example, with

    sox infile outfile gain -h bass +6

    6 dB of attenuation will be applied prior to the bass boosting effect thus ensuring that it will
    not clip. Of course, with bass, it is obvious how much headroom will be needed, but with other
    effects (e.g. rate, dither) it is not always as clear. Another advantage of using gain -h rather
    than an explicit attenuation, is that if the headroom is not used by subsequent effects, it can
    be reclaimed with gain -r, for example:

    sox infile outfile gain -h bass +6 rate 44100 gain -r

    The above effects chain guarantees never to clip nor amplify; it attenuates if necessary to
    prevent clipping, but by only as much as is needed to do so.

    Output formatting (dithering and bit-depth reduction) also requires headroom (which cannot be
    'reclaimed'), e.g.

    sox infile outfile gain -h bass +6 rate 44100 gain -rh dither

    Here, the second gain invocation, reclaims as much of the headroom as it can from the preceding
    effects, but retains as much headroom as is needed for subsequent processing.

    See also the norm and vol effects.
"""


def highpass() -> str:
    return """
highpass [-1|-2] frequency[k] [width[q|o|h|k]]
    Apply a high-pass filter with 3 dB point frequency. The filter can be either single-pole (with -1),
    or double-pole (the default, or with -2). width applies only to double-pole filters; the default
    is Q = 0.707 and gives a Butterworth response. The filters roll off at 6 dB per pole per octave
    (20 dB per pole per decade).

    See also sinc for filters with a steeper roll-off.
"""


def hilbert() -> str:
    return """
hilbert [-n taps]
    Apply an odd-tap Hilbert transform filter, phase-shifting the signal by 90 degrees.

    This is used in many matrix coding schemes and for analytic signal generation. The process is
    often written as a multiplication by i (or j), the imaginary unit.

    An odd-tap Hilbert transform filter has a bandpass characteristic, attenuating the lowest and
    highest frequencies. Its bandwidth can be controlled by the number of filter taps, which can be
    specified with -n. By default, the number of taps is chosen for a cutoff frequency of about 75 Hz.
"""


def loudness() -> str:
    return """
loudness [gain [reference]]
    Loudness control - similar to the gain effect, but provides equalisation for the human auditory
    system. See https://en.wikipedia.org/wiki/Loudness for a detailed description of loudness. The
    gain is adjusted by the given gain parameter (usually negative) and the signal equalised
    according to ISO 226 w.r.t. a reference level of 65 dB, though an alternative reference level
    may be given if the original audio has been equalised for some other optimal level. A default
    gain of -10 dB is used if a gain value is not given.

    See also the gain effect.
"""


def lowpass() -> str:
    return """
lowpass [-1|-2] frequency[k] [width[q|o|h|k]]
    Apply a low-pass filter with 3 dB point frequency. The filter can be either single-pole (with -1),
    or double-pole (the default, or with -2). width applies only to double-pole filters; the default
    is Q = 0.707 and gives a Butterworth response. The filters roll off at 6 dB per pole per octave
    (20 dB per pole per decade).

    See also sinc for filters with a steeper roll-off.
"""


def mcompand() -> str:
    return """
mcompand "attack1,decay1{,attack2,decay2} [soft-knee-dB:]in-dB1[,out-dB1]{,in-dB2,out-dB2} [gain [initial-volume-dB [delay]]]" {crossover-freq[k] "attack1,..."}
    The multi-band compander is similar to the single-band compander but the audio is first divided
    into bands using Linkwitz-Riley cross-over filters and a separately specifiable compander run on
    each band. See the compand effect for the definition of its parameters. Compand parameters are
    specified between double quotes and the crossover frequency for that band is given by
    crossover-freq; these can be repeated to create multiple bands.

    For example, the following (one long) command shows how multi-band companding is typically used
    in FM radio:

    play track1.wav gain -3 sinc 8000- 29 100 mcompand \
     "0.005,0.1 -47,-40,-34,-34,-17,-33" 100 \
     "0.003,0.05 -47,-40,-34,-34,-17,-33" 400 \
     "0.000625,0.0125 -47,-40,-34,-34,-15,-33" 1600 \
     "0.0001,0.025 -47,-40,-34,-34,-31,-31,-0,-30" 6400 \
     "0,0.025 -38,-31,-28,-28,-0,-25" \
     gain 15 highpass 22 highpass 22 sinc -n 255 -b 16 -17500 \
     gain 9 lowpass -1 17801

    The audio file is played with a simulated FM radio sound (or broadcast signal condition if the
    lowpass filter at the end is skipped). Note that the pipeline is set up with US-style 75 us
    pre-emphasis.

    See also compand for a single-band companding effect.
"""


def norm() -> str:
    return """
norm [dB-level]
    Normalise the audio. norm is just an alias for gain -n; see the gain effect for details.
"""


def overdrive() -> str:
    return """
overdrive [gain(20) [colour(20)]]
    Non linear distortion. The colour parameter controls the amount of even harmonic content in the
    over-driven output.
"""


def phaser() -> str:
    return """
phaser gain-in gain-out delay decay speed [-s|-t]
    Add a phasing effect to the audio.

    delay/decay/speed gives the delay in milliseconds and the decay (relative to gain-in) with a
    modulation speed in Hz. The modulation is either sinusoidal (-s) - preferable for multiple
    instruments, or triangular (-t) - gives single instruments a sharper phasing effect. The decay
    should be less than 0.5 to avoid feedback, and usually no less than 0.1. Gain-out is the
    volume of the output.

    For example:

    play snare.flac phaser 0.8 0.74 3 0.4 0.5 -t

    Gentler:

    play snare.flac phaser 0.9 0.85 4 0.23 1.3 -s

    A popular sound:

    play snare.flac phaser 0.89 0.85 1 0.24 2 -t

    More severe:

    play snare.flac phaser 0.6 0.66 3 0.6 2 -t
"""


def pitch() -> str:
    return """
pitch [-q] shift [segment [search [overlap]]]
    Change the audio pitch (but not tempo).

    shift gives the pitch shift as positive or negative 'cents' (i.e. 100ths of a semitone). See
    the tempo effect for a description of the other parameters.

    See also the bend, speed, and tempo effects.
"""


def reverb() -> str:
    return """
reverb [-w|--wet-only] [reverberance (50%) [HF-damping (50%) [room-scale (100%) [stereo-depth (100%) [pre-delay (0 ms) [wet-gain (0 dB)]]]]]]
    Add reverberation to the audio using the 'freeverb' algorithm. A reverberation effect is
    sometimes desirable for concert halls that are too small or contain so many people that the
    hall's natural reverberance is diminished. Applying a small amount of stereo reverb to a (dry)
    mono signal will usually make it sound more natural. See [3] for a detailed description of
    reverberation.

    Note that this effect increases both the volume and the length of the audio, so to prevent
    clipping in these domains, a typical invocation might be:

    play dry.wav gain -3 pad 0 3 reverb

    The -w option can be given to select only the 'wet' signal, thus allowing it to be processed
    further, independently of the 'dry' signal. E.g.

    play -m voice.wav "|sox voice.wav -p reverse reverb -w reverse"

    for a reverse reverb effect.
"""


def sinc() -> str:
    return """
sinc [-a att|-b beta] [-p phase|-M|-I|-L] [-t tbw|-n taps] [freqHP] [-freqLP [-t tbw|-n taps]]
    Apply a sinc kaiser-windowed low-pass, high-pass, band-pass, or band-reject filter to the
    signal. The freqHP and freqLP parameters give the frequencies of the 6 dB points of a
    high-pass and low-pass filter that may be invoked individually, or together. If both are
    given, then freqHP less than freqLP creates a band-pass filter, freqHP greater than freqLP
    creates a band-reject filter. For example, the invocations

    sinc 3k
    sinc -4k
    sinc 3k-4k
    sinc 4k-3k

    create a high-pass, low-pass, band-pass, and band-reject filter respectively.

    The default stop-band attenuation of 120 dB can be overridden with -a; alternatively, the
    kaiser-window 'beta' parameter can be given directly with -b.

    The default transition band-width of 5% of the total band can be overridden with -t (and
    tbw in Hertz); alternatively, the number of filter taps can be given directly with -n.

    If both freqHP and freqLP are given, then a -t or -n option given to the left of the
    frequencies applies to both frequencies; one of these options given to the right of the
    frequencies applies only to freqLP.

    The -p, -M, -I, and -L options control the filter's phase response; see the rate effect
    for details.
"""


def speed() -> str:
    return """
speed factor[c]
    Adjust the audio speed (pitch and tempo together). factor is either the ratio of the new
    speed to the old speed: greater than 1 speeds up, less than 1 slows down, or, if appended
    with the letter 'c', the number of cents (i.e. 100ths of a semitone) by which the pitch
    (and tempo) should be adjusted: greater than 0 increases, less than 0 decreases.

    Technically, the speed effect only changes the sample rate information, leaving the samples
    themselves untouched. The rate effect is invoked automatically to resample to the output
    sample rate, using its default quality/speed. For higher quality or higher speed
    resampling, in addition to the speed effect, specify the rate effect with the desired
    quality option.

    See also the bend, pitch, and tempo effects.
"""


def tempo() -> str:
    return """
tempo [-q] [-m|-s|-l] factor [segment [search [overlap]]]
    Change the audio playback speed but not its pitch. This effect uses the WSOLA algorithm. The
    audio is chopped up into segments which are then shifted in the time domain and overlapped
    (cross-faded) at points where their waveforms are most similar as determined by measurement
    of 'least squares'.

    By default, linear searches are used to find the best overlapping points. If the optional -q
    parameter is given, tree searches are used instead. This makes the effect work more quickly,
    but the result may not sound as good. However, if you must improve the processing speed,
    this generally reduces the sound quality less than reducing the search or overlap values.

    The -m option is used to optimize default values of segment, search and overlap for music
    processing.

    The -s option is used to optimize default values of segment, search and overlap for speech
    processing.

    The -l option is used to optimize default values of segment, search and overlap for 'linear'
    processing that tends to cause more noticeable distortion but may be useful when factor is
    close to 1.

    If -m, -s, or -l is specified, the default value of segment will be calculated based on
    factor, while default search and overlap values are based on segment. Any values you provide
    still override these default values.

    factor gives the ratio of new tempo to the old tempo, so e.g. 1.1 speeds up the tempo by
    10%, and 0.9 slows it down by 10%.

    The optional segment parameter selects the algorithm's segment size in milliseconds. If no
    other flags are specified, the default value is 82 and is typically suited to making small
    changes to the tempo of music. For larger changes (e.g. a factor of 2), 41 ms may give a
    better result. The -m, -s, and -l flags will cause the segment default to be automatically
    adjusted based on factor. For example using -s (for speech) with a tempo of 1.25 will
    calculate a default segment value of 32.

    The optional search parameter gives the audio length in milliseconds over which the algorithm
    will search for overlapping points. If no other flags are specified, the default value is
    14.68. Larger values use more processing time and may or may not produce better results. A
    practical maximum is half the value of segment. Search can be reduced to cut processing time
    at the risk of degrading output quality. The -m, -s, and -l flags will cause the search
    default to be automatically adjusted based on segment.

    The optional overlap parameter gives the segment overlap length in milliseconds. Default
    value is 12, but -m, -s, or -l flags automatically adjust overlap based on segment size.
    Increasing overlap increases processing time and may increase quality. A practical maximum
    for overlap is the value of search, with overlap typically being (at least) a little
    smaller then search.

    See also speed for an effect that changes tempo and pitch together, pitch and bend for
    effects that change pitch only, and stretch for an effect that changes tempo using a
    different algorithm.
"""


def treble() -> str:
    return """
treble gain [frequency[k] [width[s|h|k|o|q]]]
    Boost or cut the treble (upper) frequencies of the audio using a two-pole shelving
    filter with a response similar to that of a standard hi-fi's tone-controls. This is
    also known as shelving equalisation (EQ).

    gain gives the gain at whichever is the lower of ~22 kHz and the Nyquist frequency.
    Its useful range is about -20 (for a large cut) to +20 (for a large boost). Beware
    of Clipping when using a positive gain.

    If desired, the filter can be fine-tuned using the following optional parameters:

    frequency sets the filter's central frequency and so can be used to extend or reduce
    the frequency range to be boosted or cut. The default value is 3 kHz.

    width determines how steep is the filter's shelf transition. In addition to the
    common width specification methods described above, 'slope' (the default, or if
    appended with 's') may be used. The useful range of 'slope' is about 0.3, for a
    gentle slope, to 1 (the maximum), for a steep slope; the default value is 0.5.

    See also equalizer for a peaking equalisation effect.
"""


def tremolo() -> str:
    return """
tremolo speed [depth]
    Apply a tremolo (low frequency amplitude modulation) effect to the audio. The
    tremolo frequency in Hz is given by speed, and the depth as a percentage by
    depth (default 40).
"""


def vol() -> str:
    return """
vol gain [type [limitergain]]
    Apply an amplification or an attenuation to the audio signal. Unlike the -v option
    (which is used for balancing multiple input files as they enter the sox effects
    processing chain), vol is an effect like any other so can be applied anywhere, and
    several times if necessary, during the processing chain.

    The amount to change the volume is given by gain which is interpreted, according
    to the given type, as follows: if type is amplitude (or is omitted), then gain is
    an amplitude (i.e. voltage or linear) ratio, if power, then a power (i.e. wattage
    or voltage-squared) ratio, and if dB, then a power change in dB.

    When type is amplitude or power, a gain of 1 leaves the volume unchanged, less
    than 1 decreases it, and greater than 1 increases it; a negative gain inverts the
    audio signal in addition to adjusting its volume.

    When type is dB, a gain of 0 leaves the volume unchanged, less than 0 decreases
    it, and greater than 0 increases it.

    Beware of Clipping when the increasing the volume.

    The gain and the type parameters can be concatenated if desired, e.g. vol 10 dB.

    An optional limitergain value can be specified and should be a value much less
    than 1 (e.g. 0.05 or 0.02) and is used only on peaks to prevent clipping. Not
    specifying this parameter will cause no limiter to be used. In verbose mode,
    this effect will display the percentage of the audio that needed to be limited.

    See also gain for a volume-changing effect with different capabilities, and
    compand for a dynamic-range compression/expansion/limiting effect.
"""

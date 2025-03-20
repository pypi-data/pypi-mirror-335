"""
A backend for data-over-sound communication.

Original project: https://github.com/ggerganov/ggwave.
Modified by Yauheni.
"""

cimport cython

from libc.stdio cimport stderr
from cython.cimports.libc.stdlib import malloc, free
from enum import Enum

cimport cggwave


class SampleFormat(Enum):
    UNDEFINED = 0
    U8 = 1
    I8 = 2
    U16 = 3
    I16 = 4
    F32 = 5


class Protocol(Enum):
    AUDIBLE_NORMAL = 0
    AUDIBLE_FAST = 1
    AUDIBLE_FASTEST = 2
    ULTRASOUND_NORMAL = 3
    ULTRASOUND_FAST = 4
    ULTRASOUND_FASTEST = 5
    DT_NORMAL = 6
    DT_FAST = 7
    DT_FASTEST = 8
    MT_NORMAL = 9
    MT_FAST = 10
    MT_FASTEST = 11
    CUSTOM0 = 12
    CUSTOM1 = 13
    CUSTOM2 = 14
    CUSTOM3 = 15
    CUSTOM4 = 16
    CUSTOM5 = 17
    CUSTOM6 = 18
    CUSTOM7 = 19
    CUSTOM8 = 20
    CUSTOM9 = 21


class Filter(Enum):
    HANN = 0
    HAMMING = 1
    FIRST_ORDER_HIGH_PASS = 2


class OperatingMode(Enum):
    RX = 1 << 1  # =2
    TX = 1 << 2  # =4
    RX_AND_TX = RX | TX  # =6
    TX_ONLY_TONES = 1 << 3  # =8
    USE_DSS = 1 << 4  # =16


cdef class Parameters:
    cdef public cggwave.ggwave_Parameters params

    def __cinit__(
            self,
            payload_length: int | None = None,
            sample_rate_inp: float | None = None,
            sample_rate_out: float | None = None,
            sample_rate: float | None = None,
            samples_per_frame: int | None = None,
            sound_marker_threshold: float | None = None,
            sample_format_inp: SampleFormat | None = None,
            sample_format_out: SampleFormat | None = None,
            operating_mode: int | None = None,
    ) -> None:
        self.params = raw__get_default_parameters()

        if payload_length is not None:
            self.params.payloadLength = payload_length
        if sample_rate_inp is not None:
            self.params.sampleRateInp = sample_rate_inp
        if sample_rate_out is not None:
            self.params.sampleRateOut = sample_rate_out
        if sample_rate is not None:
            self.params.sampleRate = sample_rate
        if samples_per_frame is not None:
            self.params.samplesPerFrame = samples_per_frame
        if sound_marker_threshold is not None:
            self.params.soundMarkerThreshold = sound_marker_threshold
        if sample_format_inp is not None:
            self.params.sampleFormatInp = sample_format_inp.value
        if sample_format_out is not None:
            self.params.sampleFormatOut = sample_format_out.value
        if operating_mode is not None:
            self.params.operatingMode = operating_mode

    @property
    def payload_length(self) -> int:
        return self.params.payloadLength

    @property
    def sample_rate_inp(self) -> float:
        return self.params.sampleRateInp

    @property
    def sample_rate_out(self) -> float:
        return self.params.sampleRateOut

    @property
    def sample_rate(self) -> float:
        return self.params.sampleRate

    @property
    def samples_per_frame(self) -> int:
        return self.params.samplesPerFrame

    @property
    def sound_marker_threshold(self) -> float:
        return self.params.soundMarkerThreshold

    @property
    def sample_format_inp(self) -> SampleFormat:
        return SampleFormat(self.params.sampleFormatInp)

    @property
    def sample_format_out(self) -> SampleFormat:
        return SampleFormat(self.params.sampleFormatOut)

    @property
    def operating_mode(self) -> int:
        return self.params.operatingMode


def raw__get_default_parameters():
    """
    Returns default GGWave parameters.
    """

    return cggwave.ggwave_getDefaultParameters()

def raw__init(parameters: Parameters | None = None):
    """
    Initializes GGWave instance and returns its identifier.
    """

    if (parameters is None):
        parameters = Parameters()

    return cggwave.ggwave_init(parameters.params)

def raw__free(instance: int) -> None:
    """
    Frees GGWave instance.
    """
    return cggwave.ggwave_free(instance)

def raw__encode(payload: bytes | str, protocolId: int = 1, volume: int = 10, instance: int | None = None) -> bytes:
    """ Encode payload into an audio waveform.
        @param {string} payload, the data to be encoded
        @return Generated audio waveform bytes representing 16-bit signed integer samples.
    """

    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    cdef bytes data_bytes = payload

    cdef char* cdata = data_bytes

    own = False
    if (instance is None):
        own = True
        instance = raw__init(raw__get_default_parameters())

    n = cggwave.ggwave_encode(instance, cdata, len(data_bytes), protocolId, volume, NULL, 1)

    cdef bytes output_bytes = bytes(n)
    cdef char* coutput = output_bytes

    n = cggwave.ggwave_encode(instance, cdata, len(data_bytes), protocolId, volume, coutput, 0)

    if (own):
        raw__free(instance)

    return output_bytes

def raw__decode(instance: int, waveform: bytes) -> bytes | None:
    """ Analyze and decode audio waveform to obtain original payload
        @param {bytes} waveform, the audio waveform to decode
        @return The decoded payload if successful.
    """

    cdef bytes data_bytes = waveform
    cdef char* cdata = data_bytes

    cdef bytes output_bytes = bytes(256)
    cdef char* coutput = output_bytes

    rxDataLength = cggwave.ggwave_decode(instance, cdata, len(data_bytes), coutput)

    if (rxDataLength > 0):
        return coutput[:rxDataLength]

    return None

def raw__disable_log() -> None:
    """
    Disables all GGWave logging.

    It can be enabled afterwards by calling `raw__enable_log()`.
    """
    cggwave.ggwave_setLogFile(NULL);

def raw__enable_log() -> None:
    """
    Enables all GGWave logging (it's enabled by default).

    It can be disabled afterwards by calling `raw__disable_log()`.
    """
    cggwave.ggwave_setLogFile(stderr);

def raw__rx_toggle_protocol(protocolId: int, state: bool) -> None:
    """
    Toggles specific protocol ON or OFF for receiving.

    When turned off, protocol is not used for data receiving.
    """
    cggwave.ggwave_rxToggleProtocol(protocolId, state);

def raw__tx_toggle_protocol(protocolId: int, state: bool) -> None:
    """
    Toggles specific protocol ON or OFF for sending.

    When turned off, protocol is not used for data sending.
    """
    cggwave.ggwave_txToggleProtocol(protocolId, state);

def raw__rx_protocol_set_freq_start(protocolId: int, freq_start: int) -> None:
    """
    Changes start (base) frequency for speicific protocol for data receiving.
    """
    cggwave.ggwave_rxProtocolSetFreqStart(protocolId, freq_start);

def raw__tx_protocol_set_freq_start(protocolId: int, freq_start: int) -> None:
    """
    Changes start (base) frequency for speicific protocol for data sending.
    """
    cggwave.ggwave_txProtocolSetFreqStart(protocolId, freq_start);

def raw__rx_duration_frames(instance: int) -> int:
    """
    Returns number of recorded frames.
    """
    return cggwave.ggwave_rxDurationFrames(instance)

def raw__rx_receiving(instance: int) -> bool:
    """
    Returns `True` if GGWave is currently receiving message, `False` otherwise.
    """
    return cggwave.ggwave_rxReceiving(instance)

def raw__rx_analyzing(instance: int) -> bool:
    """
    Returns `True` if GGWave is currently analyzing received message, `False` otherwise.
    """
    return cggwave.ggwave_rxAnalyzing(instance)

def raw__rx_samples_needed(instance: int) -> int:
    """
    Returns amount of samples needed to decode data.
    """
    return cggwave.ggwave_rxSamplesNeeded(instance)

def raw__rx_frames_to_record(instance: int) -> int:
    """
    Returns total amount of frames to record.

    Calculated at the moment of receiving block start marker.
    Equals to `-1` if data was invalid.
    """
    return cggwave.ggwave_rxFramesToRecord(instance)

def raw__rx_frames_left_to_record(instance: int) -> int:
    """
    Returns amount of frames left until end marker is received.

    As soon as it reaches `0` analysis begins.
    """
    return cggwave.ggwave_rxFramesLeftToRecord(instance)

def raw__rx_frames_to_analyze(instance: int) -> int:
    """
    Returns total amount of frames to analyze.
    """
    return cggwave.ggwave_rxFramesToAnalyze(instance)

def raw__rx_frames_left_to_analyze(instance: int) -> int:
    """
    Returns amount of frames left until analysis is over.
    """
    return cggwave.ggwave_rxFramesLeftToAnalyze(instance)

def raw__rx_stop_receiving(instance: int) -> bool:
    """
    Stops receiving of data.

    It will be started again as soon as block start marker is received.
    """
    return cggwave.ggwave_rxStopReceiving(instance)

def raw__rx_data_length(instance: int) -> int:
    """
    Returns length of data to be received.
    """
    return cggwave.ggwave_rxDataLength(instance)

def raw__protocol_count() -> int:
    """
    Returns total amount of protocols.
    """
    return cggwave.ggwave_protocolCount()

def raw__is_dss_enabled(instance: int) -> bool:
    return cggwave.ggwave_isDSSEnabled(instance)

def raw__hz_per_sample(instance: int) -> float:
    return cggwave.ggwave_hzPerSample(instance)

def raw__heap_size(instance: int) -> int:
    return cggwave.ggwave_heapSize(instance)

def raw__tx_tones_size(instance: int) -> int:
    return cggwave.ggwave_txTonesSize(instance)

def raw__tx_get_tone(instance: int, int index) -> int:
    return cggwave.ggwave_txGetTone(instance, index)

def raw__tx_has_data(instance: int) -> bool:
    return cggwave.ggwave_txHasData(instance)

def raw__get_dss_magic(i: int) -> int:
    return cggwave.ggwave_getDSSMagic(i)

def raw__rdft(f: bytearray, n: int, wi: bytes, wf: bytes) -> None:
    cdef unsigned char *c_f = <unsigned char *>malloc(n);
    cdef unsigned char *c_wi = <unsigned char *>malloc(n);
    cdef unsigned char *c_wf = <unsigned char *>malloc(n);
    for i in range(n):
        c_f[i] = f[i]
        c_wi[i] = wi[i]
        c_wf[i] = wf[i]
    cggwave.ggwave_rdft(<float *>c_f, n, <int *>c_wi, <float *>c_wf)
    f[:] = c_f
    free(c_f);
    free(c_wi);
    free(c_wf);

def raw__fft(src: bytes, dst: bytearray, n: int, wi: bytes, wf: bytes) -> None:
    cdef unsigned char *c_src = <unsigned char *>malloc(n);
    cdef unsigned char *c_dst = <unsigned char *>malloc(n);
    cdef unsigned char *c_wi = <unsigned char *>malloc(n);
    cdef unsigned char *c_wf = <unsigned char *>malloc(n);
    src[:] = src
    for i in range(n):
        c_wi[i] = wi[i]
        c_wf[i] = wf[i]
    cggwave.ggwave_FFT(<float *>c_src, <float *>c_dst, n, <int *>c_wi, <float *>c_wf)
    dst[:] = c_dst
    free(c_src);
    free(c_dst);
    free(c_wi);
    free(c_wf);

def raw__get_ecc_bytes_for_length(int length) -> int:
    return cggwave.ggwave_getECCBytesForLength(length)


class GGWave:
    instance: int

    def __init__(self, parameters: Parameters | None = None) -> None:
        self.instance = raw__init(parameters)

    @staticmethod
    def get_default_parameters():
        """
        Returns default GGWave parameters.
        """
        return raw__get_default_parameters()

    def free(self) -> None:
        """
        Frees GGWave instance.
        """
        raw__free(self.instance)

    def encode(self, payload: bytes | str, protocol: Protocol = Protocol.ULTRASOUND_FASTEST, volume: int = 100) -> bytes:
        """ Encode payload into an audio waveform.
            @param {string} payload, the data to be encoded
            @return Generated audio waveform bytes representing 16-bit signed integer samples.
        """
        return raw__encode(payload, protocol.value, volume, self.instance)

    def decode(self, frame: bytes) -> bytes | None:
        """ Analyze and decode audio waveform to obtain original payload
            @param {bytes} waveform, the audio waveform to decode
            @return The decoded payload if successful.
        """
        return raw__decode(self.instance, frame)

    @staticmethod
    def disable_log() -> None:
        """
        Disables all GGWave logging.

        It can be enabled afterwards by calling `enable_log()`.
        """
        raw__disable_log()

    @staticmethod
    def enable_log() -> None:
        """
        Enables all GGWave logging (it's enabled by default).

        It can be disabled afterwards by calling `disable_log()`.
        """
        raw__enable_log()

    @staticmethod
    def rx_toggle_protocol(protocol: Protocol, state: bool) -> None:
        """
        Toggles specific protocol ON or OFF for receiving.

        When turned off, protocol is not used for data receiving.
        """
        raw__rx_toggle_protocol(protocol.value, state)

    @staticmethod
    def tx_toggle_protocol(protocol: Protocol, state: bool) -> None:
        """
        Toggles specific protocol ON or OFF for sending.

        When turned off, protocol is not used for data sending.
        """
        raw__tx_toggle_protocol(protocol.value, state)

    @staticmethod
    def rx_protocol_set_freq_start(protocol: Protocol, freq_start: int) -> None:
        """
        Changes start (base) frequency for speicific protocol for data receiving.
        """
        raw__rx_protocol_set_freq_start(protocol.value, freq_start)

    @staticmethod
    def tx_protocol_set_freq_start(protocol: Protocol, freq_start: int) -> None:
        """
        Changes start (base) frequency for speicific protocol for data sending.
        """
        raw__tx_protocol_set_freq_start(protocol.value, freq_start)

    def rx_duration_frames(self) -> int:
        """
        Returns number of recorded frames.
        """
        return raw__rx_duration_frames(self.instance)

    def rx_receiving(self) -> bool:
        """
        Returns `True` if GGWave is currently receiving message, `False` otherwise.
        """
        return raw__rx_receiving(self.instance)

    def rx_analyzing(self) -> bool:
        """
        Returns `True` if GGWave is currently analyzing received message, `False` otherwise.
        """
        return raw__rx_analyzing(self.instance)

    def rx_samples_needed(self) -> int:
        """
        Returns amount of samples needed to decode data.
        """
        return raw__rx_samples_needed(self.instance)

    def rx_frames_to_record(self) -> int:
        """
        Returns total amount of frames to record.

        Calculated at the moment of receiving block start marker.
        Equals to `-1` if data was invalid.
        """
        return raw__rx_frames_to_record(self.instance)

    def rx_frames_left_to_record(self) -> int:
        """
        Returns amount of frames left until end marker is received.

        As soon as it reaches `0` analysis begins.
        """
        return raw__rx_frames_left_to_record(self.instance)

    def rx_frames_to_analyze(self) -> int:
        """
        Returns total amount of frames to analyze.
        """
        return raw__rx_frames_left_to_record(self.instance)

    def rx_frames_left_to_analyze(self) -> int:
        """
        Returns amount of frames left until analysis is over.
        """
        return raw__rx_frames_left_to_record(self.instance)

    def rx_stop_receiving(self) -> bool:
        """
        Stops receiving of data.

        It will be started again as soon as block start marker is received.
        """
        return raw__rx_frames_left_to_record(self.instance)

    def rx_data_length(self) -> int:
        """
        Returns length of data to be received.
        """
        return raw__rx_frames_left_to_record(self.instance)

    @staticmethod
    def protocol_count() -> int:
        """
        Returns total amount of protocols.
        """
        return raw__protocol_count()

    def is_dss_enabled(self) -> bool:
        """
        Returns `True` if DSS is enabled, `False` otherwise.
        """
        return raw__is_dss_enabled(self.instance)

    def hz_per_sample(self) -> float:
        return raw__hz_per_sample(self.instance)

    def heap_size(self) -> int:
        return raw__heap_size(self.instance)

    def tx_tones_size(self) -> int:
        return raw__tx_tones_size(self.instance)

    def tx_get_tone(self, index: int) -> int:
        return raw__tx_get_tone(self.instance, index)

    def tx_has_data(self) -> bool:
        return raw__tx_has_data(self.instance)

    @staticmethod
    def get_dss_magic(i: int) -> int:
        return raw__get_dss_magic(i)

    @staticmethod
    def rdft(f: bytes, n: int, wi: bytes, wf: bytes) -> None:
        return raw__rdft(f, n, wi, wf)

    @staticmethod
    def fft(src: bytes, dst: bytearray, n: int, wi: bytes, wf: bytes) -> None:
        return raw__fft(src, dst, n, wi, wf)

    @staticmethod
    def get_ecc_bytes_for_length(length: int) -> int:
        return raw__get_ecc_bytes_for_length(length)


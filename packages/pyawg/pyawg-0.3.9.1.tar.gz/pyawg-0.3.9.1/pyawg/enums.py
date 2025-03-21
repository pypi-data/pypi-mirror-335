# -*- coding: utf-8 -*-

from enum import Enum


class AmplitudeUnit(Enum):
    """
    Enumeration for amplitude units.

    Attributes:
        VPP (str): Peak-to-peak voltage.
        VRMS (str): Root mean square voltage.
        DBM (str): Decibel-milliwatts.
    """

    VPP = "VPP"
    VRMS = "VRMS"
    DBM = "DBM"


class BurstModeRigol(Enum):
    """
    Enum class representing burst modes for Rigol devices.

    Attributes:
        TRIGGERED (str): Burst mode is triggered.
        INFINITY (str): Burst mode is infinite.
        GATED (str): Burst mode is gated.
    """

    TRIGGERED = "TRIG"
    INFINITY = "INF"
    GATED = "GAT"


class BurstModeSiglent(Enum):
    """
    Enum representing the burst modes for Siglent devices.

    Attributes:
        NCYC (str): Burst mode where a specific number of cycles are generated.
        GATE (str): Burst mode where the output is controlled by a gate signal.
    """

    NCYC = "NCYC"
    GATE = "GATE"


class BurstTriggerSource(Enum):
    """
    Enum class representing the source of a burst trigger.

    Attributes:
        INTERNAL (str): Represents an internal trigger source, denoted by "INT".
        EXTERNAL (str): Represents an external trigger source, denoted by "EXT".
        MANUAL (str): Represents a manual trigger source, denoted by "MAN".
    """

    INTERNAL = "INT"
    EXTERNAL = "EXT"
    MANUAL = "MAN"


class FrequencyUnit(Enum):
    """
    Enum class representing frequency units.

    Attributes:
        HZ (str): Hertz unit.
        KHZ (str): Kilohertz unit.
        MHZ (str): Megahertz unit.
    """

    HZ = "HZ"
    KHZ = "KHZ"
    MHZ = "MHZ"


class OutputLoad(Enum):
    """
    Enum class representing different types of output loads.

    Attributes:
        HZ: Represents a high impedance load.
        INF: Represents an infinite load.
    """

    HZ = "HZ"
    INF = "INF"


class Polarity(Enum):
    """
    An enumeration representing the polarity of a signal.

    Attributes:
        NORMAL (str): Represents normal polarity with the value "NORM".
        INVERTED (str): Represents inverted polarity with the value "INVT".
    """

    NORMAL = "NORM"
    INVERTED = "INVT"


class WaveformType(Enum):
    """
    Enum class representing different types of waveforms.

    Attributes:
        SINE (str): Sine waveform.
        SQUARE (str): Square waveform.
        RAMP (str): Ramp waveform.
        PULSE (str): Pulse waveform.
        NOISE (str): Noise waveform.
        DC (str): Direct Current (DC) waveform.
        ARB (str): Arbitrary waveform.
    """

    SINE = "SIN"
    SQUARE = "SQU"
    RAMP = "RAMP"
    PULSE = "PULS"
    NOISE = "NOIS"
    DC = "DC"
    ARB = "ARB"  # Arbitrary

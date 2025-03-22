import math
import numpy as np
from numba import int32, float32
from numba.experimental import jitclass

# =============================================================================
# Section: Compression Settings
# =============================================================================

CompressionSpec = [
    ("channels", int32),
    ("inCompressionThreshDb", float32),
    ("outCompressionThreshDb", float32),
    ("makeupGainDb", float32),
    ("kneeWidthDb", float32),
    ("compressionRatio", float32),
    ("lookaheadMs", float32),
    ("attackMs", float32),
    ("releaseMs", float32),
    ("sampleRate", int32),
]


@jitclass(CompressionSpec)
class CompressionSettings:
    """
    A jitclass to hold parameters for dynamic range compression.

    Attributes:
        channels (int): Number of audio channels.
        inCompressionThreshDb (float): Input compression threshold in dB.
        outCompressionThreshDb (float): Output compression threshold in dB.
        makeupGainDb (float): Makeup gain in dB.
        kneeWidthDb (float): Knee width in dB.
        compressionRatio (float): Compression ratio.
        lookaheadMs (float): Lookahead time in milliseconds.
        attackMs (float): Attack time in milliseconds.
        releaseMs (float): Release time in milliseconds.
        sampleRate (int): Audio sample rate.
    """

    def __init__(
        self,
        channels=1,
        inCompressionThreshDb=-10.0,
        outCompressionThreshDb=-10.0,
        makeupGainDb=0.0,
        kneeWidthDb=5.0,
        compressionRatio=10.0,
        lookaheadMs=1.0,
        attackMs=30.0,
        releaseMs=150.0,
        sampleRate=44100,
    ):
        self.channels = channels
        self.inCompressionThreshDb = float32(inCompressionThreshDb)
        self.outCompressionThreshDb = float32(outCompressionThreshDb)
        self.makeupGainDb = float32(makeupGainDb)
        self.kneeWidthDb = float32(kneeWidthDb)
        self.compressionRatio = float32(compressionRatio)
        self.lookaheadMs = float32(lookaheadMs)
        self.attackMs = float32(attackMs)
        self.releaseMs = float32(releaseMs)
        self.sampleRate = int32(sampleRate)


compressionSettings = None


# =============================================================================
# Section: Gain Reduction Settings
# =============================================================================


GainReductionSpec = [
    ("alphaAttack", float32),
    ("alphaRelease", float32),
    ("state", float32),
    ("maxInputLevel", float32),
    ("maxGainReduction", float32),
    ("slope", float32),
]


@jitclass(GainReductionSpec)
class GainReductionSettings:
    """
    A jitclass to hold parameters for gain reduction computation.

    Attributes:
        alphaAttack (float32): Attack coefficient.
        alphaRelease (float32): Release coefficient.
        state (float32): Current state of the gain reduction.
        maxInputLevel (float32): Maximum input level encountered.
        maxGainReduction (float32): Maximum gain reduction applied.
        slope (float32): Slope used for the gain reduction computation.
    """

    def __init__(
        self,
        alphaAttack=0.0,
        alphaRelease=0.0,
        state=0.0,
        maxInputLevel=float("-inf"),
        maxGainReduction=0.0,
        slope=0.0,
    ):
        self.alphaAttack = float32(alphaAttack)
        self.alphaRelease = float32(alphaRelease)
        self.state = float32(state)
        self.maxInputLevel = float32(maxInputLevel)
        self.maxGainReduction = float32(maxGainReduction)
        self.slope = float32(slope)


gainReductionSettings = None


# =============================================================================
# Section: Look Ahead Settings
# =============================================================================


LookAheadSpec = [
    ("delay", float32),  # delay in seconds
    ("delayInSamples", int32),  # delay in samples
    ("writePosition", int32),  # current write position in the circular buffer
    ("buffer", float32[:]),  # 1D float32 array for the circular buffer
    ("lastPushedSamples", int32),  # number of samples last pushed
]


@jitclass(LookAheadSpec)
class LookAheadSettings:
    """
    A jitclass to hold parameters for lookahead gain reduction computation.

    Attributes:
        delay (float32): The delay time in seconds.
        delayInSamples (int32): The delay time in samples.
        writePosition (int32): Current write position in the circular buffer.
        buffer (float32[:]): The circular buffer used for lookahead processing.
        lastPushedSamples (int32): The number of samples last pushed into the buffer.
    """

    def __init__(self, delay, delayInSamples, writePosition, buffer, lastPushedSamples):
        self.delay = float32(delay)
        self.delayInSamples = int32(delayInSamples)
        self.writePosition = int32(writePosition)
        self.buffer = np.asarray(buffer, dtype=np.float32)
        self.lastPushedSamples = int32(lastPushedSamples)


lookAheadSettings = None


# =============================================================================
# Section: Other Stuff
# =============================================================================


# constants
mBlockSize = 512
log2ToDb = 20 / 3.321928094887362

# envelope definitions
mEnvelope = np.zeros(mBlockSize, dtype=np.float32)

# 2D delayed input buffer
delayedInput = None


# =============================================================================
# Section: Initialization
# =============================================================================


def setSettings(
    chan, thresh, makeupGain, kneeWidth, compRatio, lookahead, attack, release, sr
):
    global compressionSettings, gainReductionSettings, lookAheadSettings, delayedInput

    compressionSettings = CompressionSettings(
        channels=chan,
        inCompressionThreshDb=thresh,
        outCompressionThreshDb=thresh + makeupGain,
        makeupGainDb=makeupGain,
        kneeWidthDb=kneeWidth,
        compressionRatio=compRatio,
        lookaheadMs=lookahead,
        attackMs=attack,
        releaseMs=release,
        sampleRate=sr,
    )

    # computing alphaAttack
    alphaAttack = 1.0 - math.exp(-1.0 / (sr * attack / 1000))

    # computing alphaRelease
    alphaRelease = 1.0 - math.exp(-1.0 / (sr * release / 1000))

    # computing slope based on compression ratio
    slope = 1 / compRatio - 1

    # Create an instance of GainReductionSettings with these computed values
    gainReductionSettings = GainReductionSettings(
        alphaAttack=alphaAttack,
        alphaRelease=alphaRelease,
        state=0.0,
        maxInputLevel=float("-inf"),
        maxGainReduction=0.0,
        slope=slope,
    )

    # lookahead delay time
    if lookahead > 0:
        delay = lookahead / 1000
    else:
        delay = 0.0

    # setting lookahead circular buffer
    delayInSamples = int(delay * sr)
    buffer = np.zeros(mBlockSize + delayInSamples, dtype=np.float32)

    # Now, create an instance of LookAheadSettings with these computed values.
    lookAheadSettings = LookAheadSettings(
        delay=delay,
        delayInSamples=delayInSamples,
        writePosition=0,
        buffer=buffer,
        lastPushedSamples=0,
    )

     # initializing delayedInput buffer
    delayedInput = np.zeros((chan, mBlockSize + delayInSamples), dtype=np.float32)

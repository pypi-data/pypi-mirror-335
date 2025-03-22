from . import definitions as d
from . import gainReduction
import numpy as np
import math
import numba


def UpdateEnvelope(audio, processed, toProcess):
    # get the range of samples for each channel from the parameters
    block = audio[:, processed : processed + toProcess]

    # compute the maximum absolute value across channels for each sample in the block
    d.mEnvelope = np.max(np.abs(block), axis=0)

    # compute the gain reduction based on the m_envelope
    gainReduction.computeGainInDecibelsFromSidechainSignal(d.mEnvelope, toProcess, d.log2ToDb, d.compressionSettings, d.gainReductionSettings)

    # quit early if there is no lookahead smoothing
    if d.compressionSettings.lookaheadMs <= 0:
        return

    # do lookahead smoothing processing, no idea how this works...
    gainReduction.pushSamples(d.mEnvelope, toProcess, d.lookAheadSettings)
    gainReduction.process(d.lookAheadSettings)
    gainReduction.readSamples(d.mEnvelope, toProcess, d.lookAheadSettings)

@numba.njit
def ApplyEnvelope(audio, mEnvelope, delayedInput, processed, toProcess, lookSettings, compressSettings):
    # get values needed from the settings
    makeupGainDb = compressSettings.makeupGainDb
    delay = lookSettings.delayInSamples
    channels = compressSettings.channels

    # loop through each channel.
    for i in range(channels):
        # get delayed input for this channel.
        delayedIn = delayedInput[i]

        # process each sample in the current block.
        for j in range(toProcess):
            # track the maximum absolute value for this channel.
            sample_val = delayedIn[j]

            # calculate the gain factor using the envelope and makeup gain.
            gain_factor = math.pow(10, 0.05 * (mEnvelope[j] + makeupGainDb))
            # apply the gain factor to the delayed sample and store the result.
            audio[i][processed + j] = sample_val * gain_factor

        # shift the delayed input buffer: move the next 'delay' samples to the start.
        delayedInput[i][:delay] = delayedIn[toProcess : toProcess + delay]

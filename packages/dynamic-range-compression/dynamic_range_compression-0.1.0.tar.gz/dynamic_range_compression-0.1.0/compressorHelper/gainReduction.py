import math
import numba

# helper functions for computing gain reduction and lookahead gain reduction

@numba.njit
def computeGainInDecibelsFromSidechainSignal(mEnvelope, numSamples, log2ToDb, compressionSettings, gainSettings):
    gainSettings.maxInputLevel = float("-inf")
    gainSettings.maxGainReduction = 0.0

    for i in range(numSamples):
        # convert the current signal to decibals
        epsilon = 1e-10
        value = abs(mEnvelope[i])
        if value < epsilon:
            value = epsilon
        levelInDecibels = log2ToDb * math.log2(value)

        # update the max input level
        if levelInDecibels > gainSettings.maxInputLevel:
            gainSettings.maxInputLevel = levelInDecibels

        # calculate the overshoot compared to the set threshold
        overShoot = levelInDecibels - compressionSettings.inCompressionThreshDb

        # apply soft-knee compression curve, applying reduction based on how far input level exceeds threshold
        gainReduction = 0.0
        kneeHalf = compressionSettings.kneeWidthDb / 2
        if overShoot <= -kneeHalf:
            gainReduction = 0.0
        elif overShoot <= kneeHalf:
            gainReduction = (
                0.5
                * gainSettings.slope
                * (overShoot + kneeHalf)
                * (overShoot + kneeHalf)
                / compressionSettings.kneeWidthDb
            )
        else:
            gainReduction = gainSettings.slope * overShoot

        # factor in attack or release
        diff = gainReduction - gainSettings.state
        if diff < 0:
            gainSettings.state += gainSettings.alphaAttack * diff
        else:
            gainSettings.state += gainSettings.alphaRelease * diff

        # apply the gain reduction
        mEnvelope[i] = gainSettings.state

        # update max gain reduction
        if gainSettings.state < gainSettings.maxGainReduction:
            gainSettings.maxGainReduction = gainSettings.state


# yeah i have no idea how the lookahead gain reduction works and looks way to hard to figure out
# shout out to Daniel Rudrich for making this
# https://github.com/audacity/audacity/blob/a96466f4924ea4c7525e1a4429d55070e685f17e/au3/libraries/lib-dynamic-range-processor/SimpleCompressor/LookAheadGainReduction.cpp


# push current samples into circular buffer
@numba.njit
def pushSamples(mEnvelope, numSamples, lookSettings):
    startIndex = 0
    blockSize1 = 0
    blockSize2 = 0
    pos = lookSettings.writePosition
    L = lookSettings.buffer.size

    if pos < 0:
        pos += L
    pos = pos % L

    if numSamples > 0:
        startIndex = pos
        blockSize1 = min(L - pos, numSamples)
        samplesLeft = numSamples - blockSize1
        blockSize2 = 0 if samplesLeft <= 0 else samplesLeft

    # Copy blockSize1 samples from d.mEnvelope into d.buffer starting at startIndex
    lookSettings.buffer[startIndex : startIndex + blockSize1] = mEnvelope[:blockSize1]

    # If blockSize2 > 0, copy the next blockSize2 samples from d.mEnvelope into the beginning of d.buffer
    if blockSize2 > 0:
        lookSettings.buffer[:blockSize2] = mEnvelope[blockSize1 : blockSize1 + blockSize2]

    lookSettings.writePosition += numSamples
    lookSettings.writePosition = lookSettings.writePosition % L

    lookSettings.lastPushedSamples = numSamples

@numba.njit
def process(lookSettings):
    nextGainReductionValue = 0.0
    step = 0.0

    index = lookSettings.writePosition - 1
    if index < 0:
        index += lookSettings.buffer.size

    size1 = 0
    size2 = 0
    if lookSettings.lastPushedSamples > 0:
        size1 = min(index + 1, lookSettings.lastPushedSamples)
        samplesLeft = lookSettings.lastPushedSamples - size1
        size2 = 0 if samplesLeft <= 0 else samplesLeft

    for i in range(size1):
        smpl = lookSettings.buffer[index]

        if smpl > nextGainReductionValue:
            lookSettings.buffer[index] = nextGainReductionValue
            nextGainReductionValue += step
        else:
            step = -smpl / lookSettings.delayInSamples
            nextGainReductionValue = smpl + step
        index -= 1

    if size2 > 0:
        index = lookSettings.buffer.size - 1

        for i in range(size2):
            smpl = lookSettings.buffer[index]

            if smpl > nextGainReductionValue:
                lookSettings.buffer[index] = nextGainReductionValue
                nextGainReductionValue += step
            else:
                step = -smpl / lookSettings.delayInSamples
                nextGainReductionValue = smpl + step
            index -= 1

    if index < 0:
        index = lookSettings.buffer.size - 1

    size1 = 0
    size2 = 0
    if lookSettings.delayInSamples > 0:
        size1 = min(index + 1, lookSettings.delayInSamples)
        samplesLeft = lookSettings.delayInSamples - size1
        size2 = 0 if samplesLeft <= 0 else samplesLeft

    breakWasUsed = False

    for i in range(size1):
        smpl = lookSettings.buffer[index]

        if smpl > nextGainReductionValue:
            lookSettings.buffer[index] = nextGainReductionValue
            nextGainReductionValue += step
        else:
            breakWasUsed = True
            break
        index -= 1

    if (not breakWasUsed) and size2 > 0:
        index = lookSettings.buffer.size - 1
        for i in range(size2):
            smpl = lookSettings.buffer[index]

            if smpl > nextGainReductionValue:
                lookSettings.buffer[index] = nextGainReductionValue
                nextGainReductionValue += step
            else:
                break
            index -= 1

@numba.njit
def readSamples(mEnvelope, numSamples, lookSettings):
    startIndex = 0
    blockSize1 = 0
    blockSize2 = 0
    pos = lookSettings.writePosition - lookSettings.lastPushedSamples - lookSettings.delayInSamples
    L = lookSettings.buffer.size

    if pos < 0:
        pos += L
    pos = pos % L

    if numSamples > 0:
        startIndex = pos
        blockSize1 = min(L - pos, numSamples)
        samplesLeft = numSamples - blockSize1
        blockSize2 = 0 if samplesLeft <= 0 else samplesLeft

    # Copy blockSize1 samples from d.buffer starting at startIndex into d.mEnvelope
    mEnvelope[:blockSize1] = lookSettings.buffer[startIndex : startIndex + blockSize1]

    # If there are wrapped samples, copy blockSize2 samples from the start of d.buffer
    if blockSize2 > 0:
        mEnvelope[blockSize1 : blockSize1 + blockSize2] = lookSettings.buffer[:blockSize2]

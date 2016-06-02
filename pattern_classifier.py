# returns pattern name for classification
def classifyResolutionPattern(versionA, versionB, mergeVersion):

    versionA = removeWhitespaceLines(versionA)
    versionB = removeWhitespaceLines(versionB)
    mergeVersion = removeWhitespaceLines(mergeVersion)

    isTakeOne = is_take_one(versionA, versionB, mergeVersion)
    isTakeOneAug = is_take_one_augmentation(versionA, versionB, mergeVersion)
    isDis = is_disregard(versionA, versionB, mergeVersion)
    isAug = is_augmentation(versionA, versionB, mergeVersion)
    isInter = is_interweaving(versionA, versionB, mergeVersion)
    isInterAug = is_interweaving_augmented(versionA, versionB, mergeVersion)

    # if sum([isTakeOne, isTakeOneAug, isDis, isAug, isInter, isInterAug]) > 1:
    #     raise TooManyPatternsError("There are too many damn patterns in this damn commit")

    if isTakeOne:
        return "TakeOne"
    elif isTakeOneAug:
        return "TakeOneAug"
    elif isDis:
        return "Disregard"
    elif isAug:
        return "Augmentation"
    elif isInter:
        return "Interweaving"
    elif isInterAug:
        return "InterweavingAug"
    else:
        return "Other"


def is_take_one(versionA, versionB, mergeVersion):

    linesA = len(versionA.split('\n'))
    linesAInMerge = 0
    for line in versionA.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(versionB.split('\n'))
    linesBInMerge = 0
    for line in versionB.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if percentLinesBInMerge > 90 and percentLinesAInMerge < 10:
        return True
    if percentLinesAInMerge > 90 and percentLinesBInMerge < 10:
        return True

    return False

def is_interweaving(versionA, versionB, mergeVersion):
    linesA = len(versionA.split('\n'))
    linesAInMerge = 0
    for line in versionA.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(versionB.split('\n'))
    linesBInMerge = 0
    for line in versionB.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):

            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if percentLinesBInMerge > 90 and percentLinesAInMerge > 90:
        return True

    return False

def is_disregard(versionA, versionB, mergeVersion):
    if len(mergeVersion) == 0:
        return True
    else:
        return False

def is_augmentation(versionA, versionB, mergeVersion):
    if is_disregard(versionA, versionB, mergeVersion):
        return False

    linesA = len(versionA.split('\n'))
    linesAInMerge = 0
    for line in versionA.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(versionB.split('\n'))
    linesBInMerge = 0
    for line in versionB.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):

            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if percentLinesBInMerge == 0 and percentLinesAInMerge == 0:
        return True

    return False

def is_take_one_augmentation(versionA, versionB, mergeVersion):
    linesA = len(versionA.split('\n'))
    linesAInMerge = 0
    for line in versionA.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(versionB.split('\n'))
    linesBInMerge = 0
    for line in versionB.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if (linesAInMerge + linesBInMerge) < len(mergeVersion.split('\n')):
        if percentLinesBInMerge > 90 and percentLinesAInMerge < 10:
            return True
        if percentLinesAInMerge > 90 and percentLinesBInMerge < 10:
            return True

    return False

def is_interweaving_augmented(versionA, versionB, mergeVersion):
    linesA = len(versionA.split('\n'))
    linesAInMerge = 0
    for line in versionA.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(versionB.split('\n'))
    linesBInMerge = 0
    for line in versionB.split('\n'):
        line = line.strip(' \t\n\r')
        if line in mergeVersion.split('\n'):

            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if (linesAInMerge + linesBInMerge) < len(mergeVersion.split('\n')):
        if percentLinesBInMerge > 90 and percentLinesAInMerge < 90:
            return True

    return False

def removeWhitespaceLines(lines):
    rtnString = ""
    for line in lines:
        line = str(line)
        if line.strip(' \t\n\r') != "":
            rtnString += line
    return rtnString
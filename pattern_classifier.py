import os, unicodedata

# returns pattern name for classification
def classifyResolutionPattern(A, B, M):

    A = formatLines(A)
    B = formatLines(B)
    M = formatLines(M)

    classificiations = []
    
    if isTakeOne(A, B, M):
        classificiations.append("TakeOne")
    if isTakeOneAugmentation(A, B, M):
        classificiations.append("TakeOneAug")
    if isDisregard(A, B, M):
        classificiations.append("Disregard")
    if isAugmentation(A, B, M):
        classificiations.append("Augmentation")
    if isInterweaving(A, B, M):
        classificiations.append("Interweaving")
    if isInterweavingAugmented(A, B, M):
        classificiations.append("InterweavingAug")

    return classificiations

def isTakeOne(A, B, M):

    linesA = len(A.split('\n'))
    linesAInMerge = 0
    for line in A.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(B.split('\n'))
    linesBInMerge = 0
    for line in B.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if percentLinesBInMerge > 80 and percentLinesAInMerge < 10:
        return True
    if percentLinesAInMerge > 80 and percentLinesBInMerge < 10:
        return True

    return False

def isInterweaving(A, B, M):
    linesA = len(A.split('\n'))
    linesAInMerge = 0
    for line in A.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(B.split('\n'))
    linesBInMerge = 0
    for line in B.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):

            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if percentLinesBInMerge > 60 and percentLinesAInMerge > 60:
        return True

    return False

def isDisregard(A, B, M):
    if len(M) == 0:
        return True
    else:
        return False

def isAugmentation(A, B, M):
    if isDisregard(A, B, M):
        return False

    linesA = len(A.split('\n'))
    linesAInMerge = 0
    for line in A.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(B.split('\n'))
    linesBInMerge = 0
    for line in B.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):

            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if percentLinesBInMerge == 0 and percentLinesAInMerge == 0:
        return True

    return False

def isTakeOneAugmentation(A, B, M):
    linesA = len(A.split('\n'))
    linesAInMerge = 0
    for line in A.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(B.split('\n'))
    linesBInMerge = 0
    for line in B.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if (linesAInMerge + linesBInMerge) < len(M.split('\n')):
        if percentLinesBInMerge > 80 and percentLinesAInMerge < 10:
            return True
        if percentLinesAInMerge > 80 and percentLinesBInMerge < 10:
            return True

    return False

def isInterweavingAugmented(A, B, M):
    linesA = len(A.split('\n'))
    linesAInMerge = 0
    for line in A.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):
            linesAInMerge += 1

    percentLinesAInMerge = (float(linesAInMerge)/linesA)*100

    linesB = len(B.split('\n'))
    linesBInMerge = 0
    for line in B.split('\n'):
        line = line.strip(' \t\n\r')
        if line in M.split('\n'):

            linesBInMerge += 1

    percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

    if (linesAInMerge + linesBInMerge) < len(M.split('\n')):
        if percentLinesBInMerge > 60 and percentLinesAInMerge < 60:
            return True

    return False

def formatLines(lines):
    if type(lines) == unicode:
        lines = unicodedata.normalize('NFKD', lines).encode('ascii','ignore')
        lines = os.linesep.join([s for s in lines.splitlines() if s])
    else:
        return lines
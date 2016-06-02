# returns pattern name for classification
def classifyResolutionPattern(versionA, versionB, mergeVersion):
    if authorA == authorB:
    	print("The author conflicted with themselves.") 
    elif authorA != authorC and authorB != authorC:
    	print("The merger is different from both authors: %s, %s, %s" % (authorA, authorB, authorC))
    elif authorA == authorB and authorB == authorC:
    	print("Author A == author B == author C")

    isDis = is_disregard(versionA, authorA, versionB, authorB, mergeVersion, mergeAuthor)
    isAug = is_augmentation(versionA, authorA, versionB, authorB, mergeVersion, mergeAuthor)
    isNuke = is_nuclear(versionA, authorA, versionB, authorB, mergeVersion, mergeAuthor)
    isInter = is_interweaving(versionA, authorA, versionB, authorB, mergeVersion, mergeAuthor)

    if sum([isDis, isAug, isNuke, isInter]) > 1:
    	raise TooManyPatternsError("There are too many damn patterns in this damn commit")

    elif isDis:
    	return "Disregard"
    elif isAug:
    	return "Augmentation"
    elif isNuke:
    	return "NUCLEAR"
    elif isInter and not isAug: # Augmentation contains interweaving. This is easier than checking for extra stuff
    	return "Interweaving"
    else:
    	raise NoPatternError("Couldn't find a conflict resolution pattern")


def is_disregard(versionA, versionB, mergeVersion):

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
		print line
		if line in mergeVersion.split('\n'):
			print line
			linesBInMerge += 1

	percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

	print percentLinesAInMerge
	print percentLinesBInMerge

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
		print line
		if line in mergeVersion.split('\n'):
			print line
			linesBInMerge += 1

	percentLinesBInMerge = (float(linesBInMerge)/linesB)*100

	print percentLinesAInMerge
	print percentLinesBInMerge

	if percentLinesBInMerge > 90 and percentLinesAInMerge < 90:
		return True

	return False

def is_augmentation(versionA, versionB, mergeVersion):
	if not is_interweaving(versionA, versionB, mergeVersion):
		return False

def is_nuclear(versionA, versionB, mergeVersion):
	return False
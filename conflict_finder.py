import os, sys
from subprocess import Popen, PIPE

def findConflicts(repo, commits):
    conflictSet = []
    old_wd = os.getcwd()
    os.chdir(repo.working_dir)

    if len(commits) < 2:
        # not enough commits for a conflict to emerge
        return conflictSet
    else:
        try:
            firstCommitStr = commits.pop().hexsha

            p = Popen(["git", "checkout", firstCommitStr], stdin=None, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            rc = p.returncode

            arguments = ["git", "merge"] + map(lambda c:c.hexsha, commits)
            p = Popen(arguments, stdin=None, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            rc = p.returncode

            if "CONFLICT" in out:
                notification_lines = [x for x in out.splitlines() if "CONFLICT" in x]
                conflict_filenames = []
                for line in notification_lines:
                    if "Merge conflict in " in line:
                        conflict_filenames.append(line.split('Merge conflict in ')[-1])
                    if "deleted in " in line:
                        conflict_filenames.append(line.split(' deleted in ')[0].split(': ')[-1])
                    else:
                        continue

                for filename in conflict_filenames:
                    conflictSet += getConflictSets(repo, filename)

                p = Popen(["git", "merge", "--abort"], stdin=None, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                rc = p.returncode
                return conflictSet

        finally:
            try:
                # Completely reset the working state after performing the merge
                p = Popen(["git", "clean", "-xdf"], stdin=None, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                rc = p.returncode
                p = Popen(["git", "reset", "--hard"], stdin=None, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                rc = p.returncode
                p = Popen(["git", "checkout", "."], stdin=None, stdout=PIPE, stderr=PIPE)
                out, err = p.communicate()
                rc = p.returncode
            finally:
                # Set the working directory back
                os.chdir(old_wd)

    return conflictSet

def getConflictSets(repo, filename):
    path = repo.working_dir + '/' + filename    
    content = open(filename, 'r').readlines()
    print("Looking at conflcit in %s" % path)

    isLeft = False
    isRight = False

    leftLines = []
    rightLines = []
    conflictSets = []
    leftSHA = None
    rightSHA = None

    for line in content:
        if isRight:
            if ">>>>>>>" not in line:
                rightLines.append(line)

                leftDict = {}
                leftDict['file'] = path
                leftDict['SHA'] = leftSHA
                leftDict['lines'] = os.linesep.join(leftLines)

                rightDict = {}
                rightDict['file'] = path
                rightDict['SHA'] = rightSHA
                rightDict['lines'] = os.linesep.join(rightLines)

                conflictSets.append([leftDict, rightDict])

            else:
                rightSHA = line.split(">>>>>>>")[1].strip()
                isRight = False
                print(path)
                print("Left: %s Right: %s" % (leftSHA, rightSHA))
                print("Left Lines:\n %s\n\n\nRightLines:\n %s\n\n\n" % (leftDict['lines'], rightDict['lines']))

        if isLeft:
            if "=======" not in line:
                leftLines.append(line)
            else:
                isRight = True
                isLeft = False

        if "<<<<<<<" in line:
            isLeft = True
            leftSHA = line.split("<<<<<<<")[1].strip()
            if leftSHA == 'HEAD':
                leftSHA = str(repo.head.commit)

    return conflictSets

def getDiff(A, B):
    # if not commit.parents:
    #     diff = commit.diff(EMPTY_TREE_SHA, create_patch=True)
    # else:
    #     diff = commit.diff(commit.parents[0], create_patch=True)

    diff = A.diff(B, create_patch=True)

    msg = ""
    for k in diff:
        try:
            msg = k.diff.decode(defenc)
        except UnicodeDecodeError:
            continue

    additions = ''.join([x[1:] for x in msg.splitlines() if x.startswith('+')])
    subtractions = ''.join([x[1:] for x in msg.splitlines() if x.startswith('-')])
    
    return additions, subtractions

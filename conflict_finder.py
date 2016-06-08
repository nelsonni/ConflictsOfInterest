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
    content = open(filename, 'r').read()

    isLeft = False
    isRight = False

    leftLines = []
    rightLines = []
    conflictSets = []

    for line in content:
        if "<<<<<<<" in line:
            isLeft = True
            leftSHA = line.split("<<<<<<<")[1].strip()
            if leftSHA == 'HEAD':
                leftSHA = str(repo.head.commit)

        elif "=======" in line:
            isRight = True
            isLeft = False
        elif ">>>>>>>" in line:
            isRight = False
            leftSHA = line.split(">>>>>>>")[1].strip()

            leftDict = {}
            leftDict['file'] = path
            leftDict['SHA'] = leftSHA
            leftDict['lines'] = leftLines.join("\n")

            rightDict = {}
            rightDict['file'] = path
            rightDict['SHA'] = rightSHA
            rightDict['lines'] = rightLines.join("\n")

            conflictSets.append([leftDict, rightDict])

        if isLeft:
            leftLines.append(line)
        if isRight:
            rightLines.append(line)
    
    # if '=======' not in content:
    #     print "STRANGENESS!: no conflict for %s" % path
    #     return []
    # elif len(content.split('=======')) > 2:
    #     print "MORE WEIRDNESS!: more than one conflict for %s" % path
    #     return []
    # else: 
    #     (left, right) = content.split('=======')
    #     print left.split("<<<<<<< ")[1]
    #     print("================================================")
    #     print right.split(">>>>>>>")[0]

    #     import pdb; pdb.set_trace()
    #     leftSHA = left.splitlines()[0].split(' ')[-1]
    #     rightSHA = right.splitlines()[-1].split(' ')[-1]
    #     if leftSHA == 'HEAD':
    #         leftSHA = str(repo.head.commit)
    #     if rightSHA == 'HEAD':
    #         rightSHA = str(repo.head.commit)
    #     left = ''.join(left.splitlines(True)[1:])       # remove first line
    #     right = ''.join(right.splitlines(True)[:-1])    # remove last line

        # leftDict = {}
        # leftDict['file'] = path
        # leftDict['SHA'] = leftSHA
        # leftDict['lines'] = left
        # rightDict = {}
        # rightDict['file'] = path
        # rightDict['SHA'] = rightSHA
        # rightDict['lines'] = right

        # return [leftDict, rightDict]
        print conflictSets
        return conflictSets
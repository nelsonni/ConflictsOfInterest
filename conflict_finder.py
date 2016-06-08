import os, sys
from subprocess import Popen, PIPE
from git.compat import defenc

def findConflicts(repo, commits):

    if len(commits) < 2:
        # not enough commits for a conflict to emerge
        return conflictSet
    else:
        output, conflict_set = proto_merge(repo, commits.pop(), commits)

    return conflict_set

def getUnresolvedMerge(repo, commit):
    A, B = commit.parents
    p = Popen(["git", "checkout", A.hexsha], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    p = Popen(["git", "branch", "-b", "VeryTemporaryBranch"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    repo.git.checkout("VeryTemporaryBranch")
    commit = repo.head.commit
    proto_merge(repo, commit, [B])


    p = Popen(["git", "branch", "-d", "VeryTemporaryBranch"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    print(out)



def getConflictSets(repo, filename):
    path = repo.working_dir + '/' + filename
    f = open(path, 'r')
    content = f.readlines()
    f.close()
    print("Looking at conflict in %s" % path)

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

def getAncestorDiff(repo, M):
    assert len(M.parents) >= 2
    A = M.parents[0]
    B = M.parents[1]

    common_ancestor = repo.merge_base([A,B], [])
    if not common_ancestor:
        return None

    return getDiff(common_ancestor[0], M)

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

    additions = [x[1:] for x in msg.splitlines() if x.startswith('+')]
    subtractions = [x[1:] for x in msg.splitlines() if x.startswith('-')]
    
    return additions, subtractions

def proto_merge(repo, base, commits):
    """Conduct a simulated merge of the given commit to a base branch

    :param base: Commit object to use for the base of the current branch prior to merge.
    :param commits: List of Commit objects to be applied on top of the base branch.
    :return: String output from 'git merge', and list of conflicting areas (containing 
        left and right) within a file.
    """
    conflict_set = []
    output = ""
    old_wd = os.getcwd()
    os.chdir(repo.working_dir)

    try:
        # Checkout branch up to the base commit
        p = Popen(["git", "checkout", base.hexsha], stdin=None, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        rc = p.returncode

        # Merge commit onto current branch at base commit
        arguments = ["git", "merge"] + map(lambda c:c.hexsha, commits)
        p = Popen(arguments, stdin=None, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        rc = p.returncode
        
        # Save output of commit
        output = out

        conflict_filenames = findConflictFilenames(output)
        for filename in conflict_filenames:
            conflict_set += getConflictSets(repo, filename)

        # Abort commit in order to allow for cleaning and reset
        p = Popen(["git", "merge", "--abort"], stdin=None, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        rc = p.returncode

        return output, conflict_set
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

def findConflictFilenames(output):
    conflict_filenames = []
    if "CONFLICT" in output:
        notification_lines = [x for x in output.splitlines() if "CONFLICT" in x]
        for line in notification_lines:
            if "Merge conflict in " in line:
                conflict_filenames.append(line.split('Merge conflict in ')[-1])
            elif "deleted in " in line:
                conflict_filenames.append(line.split(' deleted in ')[0].split(': ')[-1])
            else:
                print("Unknown CONFLICT filename detection: %s" % line)
                continue
    return conflict_filenames

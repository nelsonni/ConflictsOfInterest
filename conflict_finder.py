import os, sys
from subprocess import Popen, PIPE
from git.compat import defenc

OLD_WD = ""

def findConflicts(repo, commit):

    if len(commit.parents) < 2:
        # not enough commits for a conflict to emerge
        return []
    else:
        conflict_set = []
        output = proto_merge(repo, commit.parents[0], commit.parents[1])
        p = Popen(["git", "merge", "--abort"], stdin=None, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        rc = p.returncode
        print("output: %s" % output)

        filenames = findConflictFilenames(output)
        print("filenames:", filenames)
        for filename in filenames:
            print("finding conflict sets for: %s" % filename)
            conflict_set += getConflictSets(repo, commit, filename)

        proto_reset()
        return conflict_set

def getResolution(repo, commit):
    A, B = commit.parents
    p = Popen(["git", "checkout", A.hexsha], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    p = Popen(["git", "branch", "-b", "VeryTemporaryBranch"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    repo.git.checkout("VeryTemporaryBranch")
    VTB_commit = repo.head.commit
    out = proto_merge(repo, VTB_commit, B)
    proto_commit(out)
    VTB_head = repo.head.commit
    adds, subs = getDiff(VTB_head, commit)

    p = Popen(["git", "branch", "-d", "VeryTemporaryBranch"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    print("RESOLUTION ADDS:", adds)

    return adds

def getConflictSets(repo, commit, filename):
    """
    Requires that the filename exist in the currently branch checked out through git.
    """
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

                middleDict = {}
                middleDict['file'] = path
                middleDict['SHA'] = commit.hexsha
                middleDict['lines'] = os.linesep.join(getResolution(repo, commit))

                rightDict = {}
                rightDict['file'] = path
                rightDict['SHA'] = rightSHA
                rightDict['lines'] = os.linesep.join(rightLines)

                conflictSets.append([leftDict, middleDict, rightDict])

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

def proto_merge(repo, base, commit):
    """Conduct a merge of the given commit to a base branch

    :param base: Commit object used as the head of the branch to be merged onto.
    :param commit: Commit objects to be applied on top of the branch head.
    :return: String output from 'git merge' terminal command.
    """
    global OLD_WD
    OLD_WD = os.getcwd()
    os.chdir(repo.working_dir)

    # Checkout branch up to the base commit
    p = Popen(["git", "checkout", base.hexsha], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    # Merge commit onto current branch at base commit
    p = Popen(["git", "merge", commit.hexsha], stdin=None, stdout=PIPE, stderr=PIPE)
    merge_out, err = p.communicate()
    rc = p.returncode
    
    return merge_out

def proto_reset():
    p = Popen(["git", "clean", "-xdf"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    p = Popen(["git", "reset", "--hard"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    p = Popen(["git", "checkout", "."], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode
    os.chdir(OLD_WD)

def proto_commit(output):
    # Add conflicting file(s) to current branch
    arguments = ["git", "add"] + findConflictFilenames(output)
    p = Popen(arguments, stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

    # Commit broken merge branch
    p = Popen(["git", "commit", "-m", "will be deleted"], stdin=None, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    rc = p.returncode

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

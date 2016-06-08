import os
from subprocess import Popen, PIPE
from git.compat import defenc
import fixer

def findResolutions(repo, merge_commit):
    resolutionSets = []
    old_wd = os.getcwd()
    os.chdir(repo.working_dir)

    if len(merge_commit.parents) < 2:
        return [] # not enough commits for a conflict to emerge
    else:
        try:
            A, B = merge_commit.parents

            if '4b825dc642cb6eb9a060e54bf8d69288fbee4904' in repo.git.branch():
                repo.git.branch(["-D", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"])

            repo.git.checkout(A.hexsha)
            repo.git.branch("4b825dc642cb6eb9a060e54bf8d69288fbee4904")
            repo.git.checkout("master")
            repo.git.checkout(B.hexsha)
            repo.git.checkout("4b825dc642cb6eb9a060e54bf8d69288fbee4904")

            p = Popen(["git", "merge", B.hexsha], stdin=None, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            rc = p.returncode

            p = Popen(["git", "commit", "-m", "temp commit"], stdin=None, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            rc = p.returncode

            head_commit = repo.head.commit
            adds, subs = getDiff(head_commit, merge_commit)

            p = Popen(["git", "merge", "--abort"], stdin=None, stdout=PIPE, stderr=PIPE)
            out, err = p.communicate()
            rc = p.returncode

            repo.git.checkout("master")
            repo.git.branch(["-D", "4b825dc642cb6eb9a060e54bf8d69288fbee4904"])

            return os.linesep.join(adds)

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
                fixer.headcheck(repo)

    return resolutionSets





def getDiff(A, B):

    diff = A.diff(B, create_patch=True)

    msg = ""
    for k in diff:
        try:
            msg = k.diff.decode(defenc)
        except UnicodeDecodeError:
            continue

    additions = [str(x[1:]) for x in msg.splitlines() if x.startswith('+')]
    subtractions = [str(x[1:]) for x in msg.splitlines() if x.startswith('-')]
    
    return additions, subtractions

def proto_merge(repo, base, commit):
    """Conduct a merge of the given commit to a base branch

    :param base: Commit object used as the head of the branch to be merged onto.
    :param commit: Commit objects to be applied on top of the branch head.
    :return: String output from 'git merge' terminal command.
    """
    old_wd = os.getcwd()
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



# ============================================================================================



def getAncestorDiff(repo, M):
    assert len(M.parents) >= 2
    A = M.parents[0]
    B = M.parents[1]

    common_ancestor = repo.merge_base([A,B], [])
    if not common_ancestor:
        return None

    return getDiff(common_ancestor[0], M)
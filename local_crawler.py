from git import *
from git.compat import defenc
import inspect
import config_loader
import data_manager
import json, urllib2
import os
from subprocess import Popen, PIPE
import pattern_classifier as classifier
import puller

REPO_PATH = config_loader.get('REPO_PATH')
EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" # Git has a well-known, or at least sort-of-well-known, empty tree with this SHA1
DEBUG = True

def main():
    if DEBUG:
        repo = Repo(REPO_PATH)
        repo.git.checkout("master")

        mergesDict, commitsDict = data_manager.loadDictionaries(repo)

        for i,commitHash in enumerate(mergesDict):
            commit = commitsDict[commitHash]
            print commit
            #print getDiff(commit)
            parent1SHA, parent2SHA = mergesDict[commitHash]
            conflicts = findConflicts(repo, list(commit.parents))
            for file in conflicts:
                if len(file) < 2:
                    print "WARNING: list index out of range"
                    continue
                print classifier.classifyResolutionPattern(file[0]['lines'], file[1]['lines'], getDiff(commit))
    else:
        puller.pull_repositories()
        download_dir = config_loader.get('DOWNLOAD_PATH')
        downloadedRepos = [x[0] for x in os.walk(download_dir)][1:]
        for downloadedRepoPath in downloadedRepos:
            repo = Repo(downloadedRepoPath)
            repo.git.checkout("master")

            print "repo: %s, lang: %s" % (repo.remotes[0].url, getLang(repo))
            mergesDict, commitsDict = data_manager.loadDictionaries(repo)

            for i,commitHash in enumerate(mergesDict):
                commit = commitsDict[commitHash]
                conflicts = findConflicts(repo, list(commit.parents))
                parent1SHA, parent2SHA = mergesDict[commitHash]

                print "commit: %s, conflict count: %d" % (commit, len(conflicts))

                for file in conflicts:
                    if len(file) < 2:
                        print "WARNING: list index out of range, skipping"
                        continue
                    print classifier.classifyResolutionPattern(file[0]['lines'], file[1]['lines'], getDiff(commit)) 

def getDiff(commit):
    msg = ""
    if not commit.parents:
        diff = commit.diff(EMPTY_TREE_SHA, create_patch=True)
    else:
        diff = commit.diff(commit.parents[0], create_patch=True)

    for k in diff:
        try:
            msg = k.diff.decode(defenc)
        except UnicodeDecodeError:
            continue
    additions = ''.join([x[1:] for x in msg.splitlines() if x.startswith('+')])
    return additions

# determine the programming language most used in a repository
def getLang(repo):
    remote_url = repo.remotes[0].url
    
    # handle SSH url, else handle HTTPS url; Warning: BLACK MAGIC!!!
    if (remote_url[-4:] == '.git'):
        owner = remote_url.split(":")[-1][:-4].split("/")[-2]
        project = remote_url.split(":")[-1][:-4].split("/")[-1]
    else:
        owner = remote_url.split("/")[-2]
        project = remote_url.split("/")[-1]

    rawData = urllib2.urlopen('https://api.github.com/repos/' + owner + '/' + project + '/languages').read()
    jsonData = json.loads(rawData)
    return max(jsonData, key=jsonData.get)

def getCommit(commitsDict, SHA):
    return commitsDict[SHA]

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

                for filename in conflict_filenames:
                    conflictSet.append(getConflictSet(repo, filename))

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

def getConflictSet(repo, filename):
    path = repo.working_dir + '/' + filename    
    content = open(filename, 'r').read()
    
    if '=======' not in content:
        print "STRANGENESS!: no conflict for %s" % path
        return []
    if len(content.split('=======')) > 2:
        print "MORE WEIRDNESS!: more than one conflict for %s" % path
        s = content.split('=======')
        left = s[0]
        right = s[1]
    else: 
        (left, right) = content.split('=======')
    leftSHA = left.splitlines()[0].split(' ')[-1]
    rightSHA = right.splitlines()[-1].split(' ')[-1]
    if leftSHA == 'HEAD':
        leftSHA = str(repo.head.commit)
    if rightSHA == 'HEAD':
        rightSHA = str(repo.head.commit)
    left = ''.join(left.splitlines(True)[1:])       # remove first line
    right = ''.join(right.splitlines(True)[:-1])    # remove last line

    leftDict = {}
    leftDict['file'] = path
    leftDict['SHA'] = leftSHA
    leftDict['lines'] = left
    rightDict = {}
    rightDict['file'] = path
    rightDict['SHA'] = rightSHA
    rightDict['lines'] = right

    return [leftDict, rightDict]

# returns name of current branch
def getCurrentBranch(repo):
    return repo.git.rev_parse('HEAD', abbrev_ref=True)
    # git rev-parse --abbrev-ref HEAD

if __name__ == "__main__":
    main()
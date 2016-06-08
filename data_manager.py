import pickle, json, csv, os, shutil
import fixer

DEBUG = False

def loadDictionaries(repo):
    mergesDict = {}
    commitsDict = {}

    mergesDict = populateMergesDict(repo, mergesDict)
    commitsDict = populateCommitsDict(repo, mergesDict, commitsDict)
    
    fixer.headcheck(repo)
    return mergesDict, commitsDict

def populateCommitsDict(repo, mDict, cDict):
    """Populate commits dictionary of {SHA, git.Commit}

    :param repo: git.repo.Repo instance containing current git repository.
    :param mDict: Merge dictionary of {SHA, [parent1SHA, parent2SHA]}.
    :param cDict: Commits dictionary of {SHA, git.Commit}
    :return: Populated dictionary of {SHA, git.Commit}
    """
    branchesDict = {}
    if DEBUG: print("Populating commitsDict...")
    for merge in mDict:
        print('Finding commit: %s' % merge)
        commonBranches = sorted(branchesDict, key=branchesDict.get)
        commonBranches.reverse()
        branchName, commitObj = findCommitFromSHA(repo, merge, priorityBranches=commonBranches)

        if commitObj != None:
            cDict[merge] = commitObj
            parents = mDict[merge]

            if branchName in branchesDict:
                branchesDict[branchName] += 1
            else:
                branchesDict[branchName] = 1    
    return cDict

def populateMergesDict(repo, mDict):
# populates merge hash -> list of parent hashes dictionary
# operates similar to 'git rev-list --merges --all' command
    if DEBUG: print("Populating mergesDict...")
    commitHashes = repo.git.rev_list(merges=True, all=True).split('\n')
    for commitHash in commitHashes:
        parentsString = repo.git.rev_list(commitHash, parents=True)
        relevantLine = parentsString.split('\n')[0]
        parents = relevantLine.split(' ')[1:]
        mDict[str(commitHash)] = [str(x) for x in parents]
    return mDict

# repopulate commit hash -> commit object dictionary
def repopulateCommitsDict(repo, bDict, cDict):
    if DEBUG: print("repopulating commitsDict...")
    for commitHash in bDict.keys():
        branchName = bDict[commitHash]
        repo.git.checkout(branchName)
        commits = list(rep.iter_commits(branchName))
        for commit in commits:
            targetSHA = str(commit.hexsha)
            if commitHash == targetSHA:
                cDict[targetSHA] = commit
    return cDict

def findCommitFromSHA(repo, sha, priorityBranches=[]):
    for branchName in union(['origin/master'] + priorityBranches, findAllBranches(repo)):
        commit = findCommitInBranch(repo, sha, branchName)
        if commit != None:
            return branchName, commit
        else:
            print("Not found in %s" % branchName)

    return None, None

def findCommitInBranch(repo, sha, branchName):
    repo.git.checkout(branchName)
    commits = list(repo.iter_commits(branchName))
    for commit in commits:
        commitSHA = str(commit.hexsha)
        if sha == commitSHA:
            print("Found in %s" % branchName)   
            return commit
    return None

def findAllBranches(repo):
    branchList = []
    for r in repo.refs:
        if "origin/" in r.name:
            branchList.append(r.name)
    return branchList

def union(a, b):
    for each in b:
        if each not in a:
            a.append(each)
    return a
from git import *
import inspect
import config_loader

REPO_PATH = config_loader.get('REPO_PATH')

def main():
    repo = Repo(REPO_PATH)

    mergeSetDict = createMergeSetDict(repo)
    lookupDict = createHashToMergedCommitDict(repo, mergeSetDict)
    # print(hashToMergedCommitDict['ee746da65ab814bc1bb1863a73cac38a476b2e1a'].parents)

    for i,commit in enumerate(mergeSetDict):
        parent1 = lookupDict[mergeSetDict[commit][0]]
        parent2 = lookupDict[mergeSetDict[commit][1]]

# returns text of 
def getDiff(commit1, commit2):
	pass

def getCommit(commitDict, SHA):
    return commitDict[SHA]

def checkMergeForConflicts(repo):
    found_a_conflict = False
    unmerged_blobs = repo.index.unmerged_blobs()

    for path in unmerged_blobs:
      list_of_blobs = unmerged_blobs[path]
      for (stage, blob) in list_of_blobs:
        if stage != 0:
          found_a_conflict = true

# returns pattern name for classification
def classifyResolutionPattern(versionA, versionB, finalVersion):
    pass

# returns name of current branch
def getCurrentBranch(repo):
    return repo.git.branch()[2:]

# converts dictionary of SHAs to dictionary of commit objects filtered by merge status
def createHashToMergedCommitDict(repo, mergeSetDict):
    hashToCommitsDict = {}

    commits = list(repo.iter_commits(getCurrentBranch(repo)))
    for commit in commits:
        commitSHA = str(commit.hexsha)

        if (commitSHA == 'c7354e15ea02f8cb5d896aa4263d7bbc78567b3d'): print("parents: %s" % (mergeSetDict[commitSHA]))
        
        if commitSHA in mergeSetDict:
            hashToCommitsDict[commitSHA] = commit
        else:
            for parents in mergeSetDict.values():
                if commitSHA in parents:
                     hashToCommitsDict[commitSHA] = commit

    return hashToCommitsDict

# This identifies merges in the same way that Git's rev-list command does
def createMergeSetDict(repo):
    mergeSetDict = {}
    # git rev-list --merges --all
    commitSHAs = repo.git.rev_list(merges=True, all=True)
    commitSHAsList = commitSHAs.split('\n')

    for i, commitSHA in enumerate(commitSHAsList):
        if (i%10 == 0): print("%d" % i)
    	parentsString = repo.git.rev_list(commitSHA, parents=True)
        relevantLine = parentsString.split('\n')[0]
        parents = relevantLine.split(' ')[1:]

        mergeSetDict[str(commitSHA)] = [str(x) for x in parents]

    return mergeSetDict

if __name__ == "__main__":
    main()
from git import *
import inspect
import config_loader

REPO_PATH = config_loader.get('REPO_PATH')

def main():
    repo = Repo(REPO_PATH)
    repo.git.checkout("master")
    print getCurrentBranch(repo)

    mergeSetDict = createMergeSetDict(repo)
    lookupDict = createHashToMergedCommitDict(repo, mergeSetDict)
    # print(hashToMergedCommitDict['ee746da65ab814bc1bb1863a73cac38a476b2e1a'].parents)

    for i,commit in enumerate(mergeSetDict):
        print("%d: %s" % (i,commit))
        try:
            parent1 = lookupDict[mergeSetDict[commit][0]]
        except KeyError:
            print("Error: Key not found: %s" % mergeSetDict[commit][0])

        try:
            parent2 = lookupDict[mergeSetDict[commit][1]]
        except KeyError:
            print("Error: Key not found: %s" % mergeSetDict[commit][1])

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
    return repo.git.rev_parse('HEAD', abbrev_ref=True)
    # git rev-parse --abbrev-ref HEAD

# converts dictionary of SHAs to dictionary of commit objects filtered by merge status
def createHashToMergedCommitDict(repo, mergeSetDict):
    hashToCommitsDict = {}

    commits = list(repo.iter_commits("master"))
    for commit in commits:
        commitSHA = str(commit.hexsha)
        
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

    for commitSHA in commitSHAsList:
    	parentsString = repo.git.rev_list(commitSHA, parents=True)
        relevantLine = parentsString.split('\n')[0]
        parents = relevantLine.split(' ')[1:]

        mergeSetDict[str(commitSHA)] = [str(x) for x in parents]

    return mergeSetDict

if __name__ == "__main__":
    main()
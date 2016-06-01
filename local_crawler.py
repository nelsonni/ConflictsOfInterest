from git import *
import inspect

REPO_PATH = "/home/nelsonni/Workspace/FreeCodeCamp"

def main():
    repo = Repo(REPO_PATH)

    mergeSetDict = createParentDict(repo)
    lookupDict = createHashToMergedCommitDict(repo, parentDict)
    # print(hashToMergedCommitDict['ee746da65ab814bc1bb1863a73cac38a476b2e1a'].parents)

    for commit in mergeSetDict:
        

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
def createHashToMergedCommitDict(repo, parentDict):
    hashToCommitsDict = {}

    commits = list(repo.iter_commits(getCurrentBranch(repo)))
    for commit in commits:
        commitSHA = str(commit.hexsha)
        
        if commitSHA in parentDict:
            hashToCommitsDict[commitSHA] = commit
        else:
            for parents in parentDict.values():
                if commitSHA in parents:
                     hashToCommitsDict[commitSHA] = commit

    return hashToCommitsDict

# This identifies merges in the same way that Git's rev-list command does
def createParentDict(repo):
    parentDict = {}
    # git rev-list --merges --all
    commitSHAs = repo.git.rev_list(merges=True, all=True)
    commitSHAsList = commitSHAs.split('\n')

    for commitSHA in commitSHAsList:
        print("commit: %s" % commitSHA)
    	parentsString = repo.git.rev_list(commitSHA, parents=True)
    	relevantLine = parentsString.split('\n')[0]
    	parents = relevantLine.split(' ')[1:]

        parentDict[commitSHA] = parents

    return parentDict

if __name__ == "__main__":
    main()
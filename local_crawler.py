from git import *
import inspect

REPO_PATH = "/Users/Shane/Documents/FreeCodeCamp"

def main():
    repo = Repo(REPO_PATH)

    # parentDict = {}
    # parentDict['ee746da65ab814bc1bb1863a73cac38a476b2e1a'] = ['704f757cbb3749889778584a8e1d91a6f630fbd0', 'e0867ec556647f4fa4a505f6d1a548b7079fcd73']
    parentDict = createParentDict(repo)
    hashToMergedCommitDict = createHashToMergedCommitDict(repo, parentDict)
    # print(hashToMergedCommitDict['ee746da65ab814bc1bb1863a73cac38a476b2e1a'].parents)

def getDiff(commit1, commit2):
	pass

def classifyResolutionPattern(versionA, versionB, finalVersion):
    pass

def findCommonAnscestor(commit1, commit2):
    pass

def getCommit(repo, sha):
    pass

def getCurrentBranch(repo):
    return repo.git.branch()[2:]

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

# This identifies merges in the same way that Git's rev-list cmd does
def createParentDict(repo):
    parentDict = {}
    # git rev-list --merges --all
    commitSHAs = repo.git.rev_list(merges=True, all=True)
    commitSHAsList = commitSHAs.split('\n')

    for commitSHA in commitSHAsList:
    	parentsString = repo.git.rev_list(commitSHA, parents=True)
    	relevantLine = parentsString.split('\n')[0]
    	parents = relevantLine.split(' ')[1:]

        parentDict[commitSHA] = parents

    return parentDict

if __name__ == "__main__":
    main()
from git import *
import inspect
import config_loader
import json, urllib2

REPO_PATH = config_loader.get('REPO_PATH')
# REPO_PATH = "/Users/Shane/Dropbox/ScubaSteveMath"

def main():
    repo = Repo(REPO_PATH)
    repo.git.checkout("master")

    print findCommitFromSHA(repo, "e4e443c906538663d16182f1b8fb41d96f229a70")

    # mergeSetDict = createMergeSetDict(repo)
    # lookupDict = createHashToMergedCommitDict(repo, mergeSetDict)

    # for i,commitHash in enumerate(mergeSetDict):
    #     print("%d: %s" % (i,commitHash))
    #     commit = lookupDict[commitHash]
    #     parent1SHA, parent2SHA = mergeSetDict[commitHash]


def getLang(repo):
# get top programming language for repository
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

def findAllBranches(repo):
    branchList = []
    for r in repo.refs:
        if "origin/" in r.name:
            branchList.append(r.name)
    return branchList

def findCommitFromSHA(repo, sha):

    repo.git.checkout("master")
    commits = list(repo.iter_commits("master"))
    for commit in commits:
        commitSHA = str(commit.hexsha)
        if sha == commitSHA:
            return commit

    print("Not found in master")

    for branchName in findAllBranches(repo):
        repo.git.checkout(branchName)
        commits = list(repo.iter_commits(branchName))
        for commit in commits:
            commitSHA = str(commit.hexsha)
            if sha == commitSHA:
                return commit
        print("Not found in %s" % branchName)
        
    return None

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
from git import *
import inspect
import config_loader
import data_manager
import json, urllib2

# REPO_PATH = config_loader.get('REPO_PATH')
REPO_PATH = "/Users/Shane/Dropbox/ScubaSteveMath"

def main():
    project = REPO_PATH.split('/')[-1]
    repo = Repo(REPO_PATH)
    repo.git.checkout("master")

    try:
        mergesDict = data_manager.PersistentDict.load(open('data/'+project+'.merges.json', 'wb'))
    except Exception:
        mergesDict = data_manager.PersistentDict('data/'+project+'.merges.json', 'c', format='json')
        populateMergesDict(repo, mergesDict)

    try:
        commitsDict = data_manager.PersistentDict.load(open('data/'+project+'.commits.json', 'wb'))
    except Exception:
        commitsDict = data_manager.PersistentDict('data/'+project+'.commits.json', 'c', format='json')
        populateCommitsDict(repo, mergesDict, commitsDict)
        
    #print findCommitFromSHA(repo, "e4e443c906538663d16182f1b8fb41d96f229a70")

    # diffDat(repo, mergesDict, lookupDict)

    # for i,commitHash in enumerate(mergeSetDict):
    #     # print("%d: %s" % (i,commitHash))
    #     commit = lookupDict[commitHash]
    #     # print commit.message
    #     print isMergeConflict(repo, commit.parents[0], commit.parents[1])
    #     repo.delete_head('commit1') 
    #     parent1SHA, parent2SHA = mergeSetDict[commitHash]

    mergesDict.sync()
    commitsDict.sync()

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

def diffDat(repo, mergesDict, lookupDict):
    import random
    a = git.repo.to_commit(random.choice(lookupDict.keys()))
    b = random.choice(lookupDict.keys())
    print("type(a): %s, type(b): %s" % (type(a), type(b)))
    print("lookupDict: %s" % type(lookupDict.keys()))
    #print Diffable.diff(a, b)

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

def getCommit(commitsDict, SHA):
    return commitsDict[SHA]

def isMergeConflict(repo, commit1, commit2):
    master = repo.heads.master 
    new_branch = repo.create_head('commit1')  
    new_branch.commit = commit1
    merge_base = repo.merge_base(new_branch, master)
    repo.index.merge_tree(master, base=merge_base)
    # repo.delete_head('commit1') 

    return checkMergeForConflicts(repo)


def checkMergeForConflicts(repo):
    found_a_conflict = False
    unmerged_blobs = repo.index.unmerged_blobs()
    print unmerged_blobs

    for path in unmerged_blobs:
      list_of_blobs = unmerged_blobs[path]
      for (stage, blob) in list_of_blobs:
        if stage != 0:
          found_a_conflict = True
    return found_a_conflict

# returns pattern name for classification
def classifyResolutionPattern(versionA, versionB, finalVersion):
    pass

# returns name of current branch
def getCurrentBranch(repo):
    return repo.git.rev_parse('HEAD', abbrev_ref=True)
    # git rev-parse --abbrev-ref HEAD

# populates commit SHA -> commit object dictionary for merge-related commits (parent and merge)
def populateCommitsDict(repo, mergesDict, commitsDict):
    print("Populating commitsDict for %s..." % repo.active_branch)
    commits = list(repo.iter_commits("master"))
    for commit in commits:
        commitSHA = str(commit.hexsha)
        
        if commitSHA in mergesDict:
            commitsDict[commitSHA] = commit
        else:
            for parents in mergesDict.values():
                if commitSHA in parents:
                     commitsDict[commitSHA] = commit

# populates merge SHA -> parent SHA dictionary, similar to 'git rev-list --merges --all' command
def populateMergesDict(repo, mergesDict):
    print("Populating mergesDict for %s..." % repo.active_branch)
    commitSHAs = repo.git.rev_list(merges=True, all=True)
    commitSHAsList = commitSHAs.split('\n')
    for commitSHA in commitSHAsList:
        parentsString = repo.git.rev_list(commitSHA, parents=True)
        relevantLine = parentsString.split('\n')[0]
        parents = relevantLine.split(' ')[1:]
        mergesDict[str(commitSHA)] = [str(x) for x in parents]

if __name__ == "__main__":
    main()
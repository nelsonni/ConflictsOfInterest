from git import *
import inspect
import config_loader
import data_manager
import json, urllib2
import os
from subprocess import Popen, PIPE

REPO_PATH = config_loader.get('REPO_PATH')

def main():
    project = REPO_PATH.split('/')[-1]
    repo = Repo(REPO_PATH)
    repo.git.checkout("master")

    mergesDict, commitsDict = data_manager.loadDictionaries(repo)


    for i,commitHash in enumerate(mergesDict):
        # print("%d: %s" % (i,commitHash))
        commit = commitsDict[commitHash]
        print commit
        print does_merge_have_conflict(repo, list(commit.parents))
        parent1SHA, parent2SHA = mergesDict[commitHash]

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

# returns text of 
def getDiff(commit1, commit2):
    pass

def getCommit(commitsDict, SHA):
    return commitsDict[SHA]

def does_merge_have_conflict(repo,commits):
  old_wd = os.getcwd()
  os.chdir(repo.working_dir)

  if len(commits) < 2:
    return False
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
        p = Popen(["git", "merge", "--abort"], stdin=None, stdout=PIPE, stderr=PIPE)
        out, err = p.communicate()
        rc = p.returncode
        return True

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

# def isMergeConflict(repo, commit):
#     repo.delete_head('commit2') 
#     parent1, parent2 = commit.parents
#     print('Checking if it\'s a conflict: %s' % commit.hexsha)
#     master = repo.heads.master 
#     master.checkout(commit.hexsha)
#     new_branch = repo.create_head('commit2')  
#     new_branch.commit = parent2
#     merge_base = repo.merge_base(new_branch, master)
#     repo.index.merge_tree(master, base=merge_base)
#     # repo.delete_head('commit1') 

#     return checkMergeForConflicts(repo)


# def checkMergeForConflicts(repo):
#     found_a_conflict = False
#     unmerged_blobs = repo.index.unmerged_blobs()
#     print unmerged_blobs

#     for path in unmerged_blobs:
#       list_of_blobs = unmerged_blobs[path]
#       for (stage, blob) in list_of_blobs:
#         if stage != 0:
#           found_a_conflict = True
#     return found_a_conflict

# returns pattern name for classification
def classifyResolutionPattern(versionA, versionB, finalVersion):
    pass

# returns name of current branch
def getCurrentBranch(repo):
    return repo.git.rev_parse('HEAD', abbrev_ref=True)
    # git rev-parse --abbrev-ref HEAD

if __name__ == "__main__":
    main()
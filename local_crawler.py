from git import *
import inspect
import config_loader
import data_manager
import json, urllib2
import os
from subprocess import Popen, PIPE
import pattern_classifier as classifier

REPO_PATH = config_loader.get('REPO_PATH')

def main():
  # a = "aaa\nbbb\nccc\nddd\neee\nfff\nggg\nhhh\niii"
  # b = "jjj\nkkk\nlll\nmmm\nnnn\no\np\nq\nr\ns\nt\nu\nv\nw\nx\ny\nz"
  # m = "jjj\nkkk\nlll\nmmm\nnnn\no\np\nq\nr\ns\nt\nu\nv\nw\nx\ny\nz\n"
  # print classifier.classifyResolutionPattern(a, b, m)
  project = REPO_PATH.split('/')[-1]
  repo = Repo(REPO_PATH)
  repo.git.checkout("master")

  mergesDict, commitsDict = data_manager.loadDictionaries(repo)

  for i,commitHash in enumerate(mergesDict):
      # print("%d: %s" % (i,commitHash))
      commit = commitsDict[commitHash]
      print commit
      parent1SHA, parent2SHA = mergesDict[commitHash]
      if len(findConflicts(repo, list(commit.parents))) > 0:
          print "conflicts are multiplying"
          #getDiff(commitsDict[parent1SHA], commitsDict[parent2SHA])

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

# returns text of 
def getDiff(commit1, commit2):
    diff = commit1.diff(commit2)
    added_changes = diff.iter_change_type('A')
    modified_changes = diff.iter_change_type('M')
    print("added_changes:",added_changes)
    print("modified_changes:",modified_changes)

    sections = get_diff_sections(commit1, commit2)
    for i,s in enumerate(sections):
        print("section %d:" % i)
        print("first_line: %s" % s['first_line'])
        print("lines_before: %s" % s['lines_before'])
        print("lines_after: %s" % s['lines_after'])
        print("start_index: %s" % s['start_index'])
        for l in s['lines']:
            print("%s" % l.rstrip())

    for x in commit1.diff(commit2):
        if x.a_blob is not None:
            print "a_blob:",x.a_blob.path
            # print "inspection(a_blob):",
            # for m in inspect.getmembers(x.a_blob):
            #     print m
        else:
            print "a_blob:",x.a_blob
        if x.b_blob is not None:
            print "b_blob:",x.b_blob.path
        else:
            print "b_blob:",x.b_blob

def get_diff_sections(current, previous):
        word_diff = {"word-diff":"porcelain"}
        diff = previous.diff(current.hexsha, create_patch=True, **word_diff)[0].diff
        diff_lines = diff.splitlines()[2:]
        sections = []
        previous_i = 0
        for i, line in enumerate(diff_lines):
            if line.startswith('@'):
                section_info = line.split(' ')
                section_before = section_info[1].split(',')
                section_after = section_info[2].split(',')

                num_lines_before = 0 if len(section_before) == 1 else section_before[1]
                num_lines_after = 0 if len(section_after) == 1 else section_after[1]
                first_line = max(0, int(section_after[0][1:]))
                sections.append({'first_line': first_line, 'lines_before': num_lines_before, 'lines_after': num_lines_after, 'start_index': i + 1})
                previous_i = i
            if line.startswith('~'):
                diff_lines[i] = " \n"
        # Set the lines for each section
        # THIS IS THE ONLY WAY I COULD FIGURE OUT HOW TO DO IT
        # I'm sorry
        end_index = len(diff_lines)
        for i, section in enumerate(reversed(sections)):
            sections[-1-i]['lines'] = diff_lines[section['start_index']:end_index]
            section['lines'].pop()
            end_index = section['start_index'] - 1

        return sections

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
                conflict_filenames = [x.split('Merge conflict in ')[-1] for x in notification_lines]
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
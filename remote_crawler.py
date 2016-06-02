#!/usr/bin/env python

import time, sys
import config_loader
import notifier
from github import Github, GithubException
from datetime import datetime
import inspect

GITHUB_AUTH = config_loader.get('GITHUB_AUTH')
GMAIL_AUTH = config_loader.get('GMAIL_AUTH')
NOTIFY = config_loader.get('NOTIFY')
SLEEP_TIME_SEC = config_loader.get('SLEEP_TIME_SEC')

BANNED = [  'legacy-homebrew', 'gitignore', 'You-Dont-Know-JS', 'Font-Awesome',
            'free-programming-books', 'html5-boilerplate', 'the-art-of-command-line']

f = open("out.csv", "w")

def main():
    global github, repo_count
    
    github = Github(GITHUB_AUTH['username'], GITHUB_AUTH['password'])
    repo_count = 0    

    #run()


def run():
    global github, repo_count

    try:
        for repo in github.search_repositories("", stars=">1", sort="stars", order="desc"):
            
            if repo.name in BANNED:
                continue # skip repos in the banned list

            repo_count += 1
            print("%d - project: %s" % (repo_count, repo.full_name))
            merges = 0

            print("Getting all commits from: %s" % repo.full_name)
            allCommits = getAllCommits(repo)
            mergedCommits = getMergedCommits(allCommits)

            f.write(repo.name + "," + ",".join([mergedCommit.sha for mergedCommit in mergedCommits]) + "\n")
            print("\tmerges: %d" % (merges))


    except GithubException, exception:
        timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        notice = "Github Exception received by crawler.py on %s.\nExamined %d repositories.\n\nException: %s" % (timestamp, repo_count, exception)
        # for recipient in NOTIFY:
            # notifier.send_notice(GMAIL_AUTH[0], GMAIL_AUTH[1], "CS566_FinalProject failure detected", recipient, notice)
        print(notice)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def getMergedCommits(commitList):
    mergedCommits = []
    for commit in allCommits:
        parents = [parent.sha for parent in commit.parents]
        if len(parents) > 2:
            mergedCommits.append(commit)
            merges += 1

    return mergedCommits

def getAllCommits(repo):
    numCommitsInPage = 30 #Pagination is 30 per page 
    currentPage = 0
    allCommits = []
    
    while numCommitsInPage > 0:
        remainingRate = github.get_rate_limit().rate.remaining
        if remainingRate < 100:
            print("Sleeping for %d seconds to replenish rate limit" % SLEEP_TIME_SEC)
            time.sleep(SLEEP_TIME_SEC) # sleep for 1 hour to allow rate limit to replenish
            remainingRate = github.get_rate_limit().rate.remaining

        commits = [c.commit for c in repo.get_commits().get_page(currentPage)]
        numCommitsInPage = len(commits)
        allCommits += commits

        sys.stdout.write("\rCommits Downloaded: %d, API Rate Remaining: %d" % (len(allCommits), github.get_rate_limit().rate.remaining))
        sys.stdout.flush()

        currentPage += 1

    return allCommits


if __name__ == "__main__":
    main()
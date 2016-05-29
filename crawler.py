#!/usr/bin/env python

import time, sys
# import notifier
from github import Github, GithubException
from datetime import datetime
import inspect

# Configure with the appropriate user information before executing this script
GITHUB_AUTH = ('smckee6192', 'barefoot1') # Github username and password (or token)
GMAIL_AUTH = ('username', 'password') # Gmail username and password (or token)
NOTIFY = ['email_addr1', 'email_addr2'] # Email addresses to receive notifications
SLEEP_TIME_SEC = 3600

BANNED = [  'legacy-homebrew', 'gitignore', 'You-Dont-Know-JS', 'Font-Awesome',
            'free-programming-books', 'html5-boilerplate', 'the-art-of-command-line']

def main():
    global github, repo_count
    github = Github(GITHUB_AUTH[0], GITHUB_AUTH[1])
    repo_count = 0    

    run()


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

            for commit in allCommits:
                # commitMembers = inspect.getmembers(commit.tree)
                # for each in commit.tree.raw_data:
                #     print each
                # import pdb; pdb.set_trace()
                parents = [parent.sha for parent in commit.parents]
                if len(parents) > 2:
                    print commit.message
                    merges += 1
                    #print("\t%s %s %s" % (commit.message, commit.sha, commit.author.name))
            print("\tmerges: %d" % (merges))

            if repo_count % 10 == 0:
                print "API rate remaining: %d" % github.get_rate_limit().rate.remaining
            if github.get_rate_limit().rate.remaining < 100:
                print("Sleeping for %d seconds to replenish rate limit" % SLEEP_TIME_SEC)
                time.sleep(SLEEP_TIME_SEC) # sleep for 1 hour to allow rate limit to replenish

            currentPage += 1

    except GithubException, exception:
        timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        notice = "Github Exception received by crawler.py on %s.\nExamined %d repositories.\n\nException: %s" % (timestamp, repo_count, exception)
        # for recipient in NOTIFY:
            # notifier.send_notice(GMAIL_AUTH[0], GMAIL_AUTH[1], "CS566_FinalProject failure detected", recipient, notice)
        print(notice)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def getAllCommits(repo):
    numCommitsInPage = 30 #Pagination is 30 per page 
    currentPage = 0
    allCommits = []
    
    while numCommitsInPage > 0:
        commits = [c.commit for c in repo.get_commits().get_page(currentPage)]
        numCommitsInPage = len(commits)
        allCommits += commits
        sys.stdout.write("\rCommits Downloaded: %d" % len(allCommits))
        sys.stdout.flush()

        currentPage += 1

    return allCommits


if __name__ == "__main__":
    main()
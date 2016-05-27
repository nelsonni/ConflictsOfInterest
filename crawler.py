#!/usr/bin/env python

import getpass
import notifier
from github import Github
from datetime import datetime

# from os import walk
# import inspect

BANNED = ['legacy-homebrew', 'gitignore', 'You-Dont-Know-JS', 'Font-Awesome', 'free-programming-books', 'html5-boilerplate', 'the-art-of-command-line']
LIMIT = 40 # number of projects to examine

# nnelson8675 
# pgcfvjahocybedch

# github.GithubException.GithubException: 403 {u'documentation_url': u'https://developer.github.com/v3/#rate-limiting', u'message': u"API rate limit exceeded for 128.193.154.145. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)"}

# g = Github(getpass.get_user(), getpass.getpass())

notifier.test_notice()

try:
	i = 0
	for repo in g.search_repositories("", stars=">1", sort="stars", order="desc"):
		if repo.name in BANNED:
			continue
		else:
			i += 1
		
		print("%d - project: %s" % (i, repo.full_name))

		merges = 0
		commits = [c.commit for c in repo.get_commits().get_page(0)]
		for commit in commits:
			parents = [parent.sha for parent in commit.parents]
			if len(parents) > 1:
				merges += 1
				#print("\t%s %s %s" % (commit.message, commit.sha, commit.author.name))
		print("\tmerges: %d" % (merges))

		if i >= LIMIT:
			break
	break
except 
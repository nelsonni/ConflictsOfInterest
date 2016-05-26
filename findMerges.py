from github import Github
from os import walk
import getpass
# import inspect

BANNED = ['legacy-homebrew', 'gitignore', 'You-Dont-Know-JS', 'Font-Awesome', 'free-programming-books', 'html5-boilerplate', 'the-art-of-command-line']
LIMIT = 40 # number of projects to examine

g = Github('nelsonni', 'd3a75790847df1c494134bac7d1d785e9249bbc3')

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
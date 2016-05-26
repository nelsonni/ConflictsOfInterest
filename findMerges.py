from github import Github
import getpass
# import inspect

g = Github("smckee6192", getpass.getpass())
# g = Github("smckee6192", "")
repo = g.get_repo("jmaxfield21/ScubaSteveMath")
commits = [c.commit for c in repo.get_commits().get_page(0)]
for commit in commits:
	parents = [parent.sha for parent in commit.parents]
	if len(parents) > 1:
		print(commit.message)
		print(commit.sha)
		print(commit.author.name)
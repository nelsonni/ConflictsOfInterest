from git import Repo
import urllib2
import json

repoData = urllib2.urlopen('https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc').read()
jsonData = json.loads(repoData)
repos = []

banned = ['legacy-homebrew', 'gitignore', 'You-Dont-Know-JS', 'Font-Awesome', 'free-programming-books', 'html5-boilerplate', 'the-art-of-command-line']

for each in jsonData['items']:
    if each['name'] not in banned:
        repos.append( (each['name'], each['html_url']) )

for idx,r in enumerate(repos):
    print("%d - url: %s, folder: /Users/nelsonni/Downloads/%s" % (idx + 1, r[1], r[0]))
    url = r[1]
    path = "/Users/Shane/Downloads/" + r[0]
    Repo.clone_from(url, path)
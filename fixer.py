# except GitCommandError:
#     log("GitCommandError: Your repo is probably in a bad state. Try:")
#     log("git fetch origin")
#     log("git reset --hard origin/master")
#     log("git clean -d -f")
#     log("git checkout master")

def headcheck(repo):
    if repo.head.is_detached:
        repo.git.fetch('origin')
        repo.git.reset(['--hard', 'origin/master'])
        repo.git.clean(['-d', '-f'])
        repo.git.checkout('master')
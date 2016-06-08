
def headcheck(repo):
    if repo.head.is_detached:
        repo.git.checkout('master')
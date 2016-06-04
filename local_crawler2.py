import os, sys, time
import json, urllib2
from datetime import datetime
from subprocess import Popen, PIPE

# GitPython library
from git import *
from git.compat import defenc

import config_loader as config
import pattern_classifier as classifier
import git_puller as puller
import data_manager
import notifier
#import inspect

NOTIFY = False
EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" # Git has an empty tree with this SHA1
REPO_PATH = config.get('REPO_PATH')
PROJECT = None

def main():
    'Evaluates project to locate merges and merge conflicts within the Git history; return True if successful, otherwise False'
    try:
        project_path = REPO_PATH + PROJECT
        repo = Repo(project_path)
        execute(repo)
        return True

    except (NoSuchPathError, InvalidGitRepositoryError):
        error = sys.exc_info()[0].__name__
        log("%s on %s" % (error, project_path))
        return False

    except:
        error = sys.exc_info()[0].__name__
        log("Unexpected error: %s" % (error))
        return False

def execute(repo):
    repo.git.checkout("master")
    print("Off to the mining races on %s..." % PROJECT)

def log(message):
    ts = timestamp()
    print("%s: %s" % (ts, message))
    # TODO: output log message to <project.log> files
    if NOTIFY: 
        notifier.error_notice(ts, PROJECT, message, os.path.basename(__file__))

def timestamp():
    return datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ArgumentError: %s requires 1 argument" % os.path.basename(__file__))
        print("\tUsage: 'python %s <project_name>'" % os.path.basename(__file__))
        sys.exit(2)
    PROJECT = sys.argv[1]
    main()
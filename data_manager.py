import pickle, json, csv, os, shutil

DEBUG = False

def loadDictionaries(repo):
    # try:
    #     mergesDict = data_manager.PersistentDict.load(open('data/'+project+'.merges.json', 'wb'))
    # except Exception:
    #     mergesDict = data_manager.PersistentDict('data/'+project+'.merges.json', 'c', format='json')
    mergesDict = {}
    commitsDict = {}
    mergesDict = populateMergesDict(repo, mergesDict)
    commitsDict = populateCommitsDict(repo, mergesDict, commitsDict)

    # try:
    #     branchDict = data_manager.PersistentDict.load(open('data/'+project+'.branch.json', 'wb'))
    # except Exception:
    #     lookupDict = data_manager.PersistentDict('data/'+project+'.branch.json', 'c', format='json')

    # mergesDict.sync()
    # commitsDict.sync()
    
    return mergesDict, commitsDict

# repopulate commit hash -> commit object dictionary
def repopulateCommitsDict(repo, bDict, cDict):
    if DEBUG: print("repopulating commitsDict...")
    for commitHash in bDict.keys():
        branchName = bDict[commitHash]
        repo.git.checkout(branchName)
        commits = list(rep.iter_commits(branchName))
        for commit in commits:
            targetSHA = str(commit.hexsha)
            if commitHash == targetSHA:
                cDict[targetSHA] = commit
    return cDict


def findCommitFromSHA(repo, sha):
    repo.git.checkout("master")
    commits = list(repo.iter_commits("master"))
    for commit in commits:
        commitSHA = str(commit.hexsha)
        if sha == commitSHA:
            return commit
    print("Not found in master")
    for branchName in findAllBranches(repo):
        repo.git.checkout(branchName)
        commits = list(repo.iter_commits(branchName))
        for commit in commits:
            commitSHA = str(commit.hexsha)
            if sha == commitSHA:
                return commit
        print("Not found in %s" % branchName)    
    return None

def findAllBranches(repo):
    branchList = []
    for r in repo.refs:
        if "origin/" in r.name:
            branchList.append(r.name)
    return branchList

# populates commit hash -> commit object dictionary
def populateCommitsDict(repo, mDict, cDict):
    if DEBUG: print("Populating commitsDict...")
    for merge in mDict:
        print('Finding commit: %s' % merge)
        cDict[merge] = findCommitFromSHA(repo, merge)
        parents = mDict[merge]
        for parent in parents:
            print('\tFinding parent: %s' % parent)
            if parent not in cDict:
                cDict[parent] = findCommitFromSHA(repo, parent)        
    return cDict

# populates merge hash -> list of parent hashes dictionary
# operates similar to 'git rev-list --merges --all' command
def populateMergesDict(repo, mDict):
    if DEBUG: print("Populating mergesDict...")
    commitHashes = repo.git.rev_list(merges=True, all=True).split('\n')
    for commitHash in commitHashes:
        parentsString = repo.git.rev_list(commitHash, parents=True)
        relevantLine = parentsString.split('\n')[0]
        parents = relevantLine.split(' ')[1:]
        mDict[str(commitHash)] = [str(x) for x in parents]
    return mDict

class PersistentDict(dict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.

    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    '''

    def __init__(self, filename, flag='c', mode=None, format='pickle', *args, **kwds):
        self.flag = flag                    # r=readonly, c=create, or n=new
        self.mode = mode                    # None or an octal triple like 0644
        self.format = format                # 'csv', 'json', or 'pickle'
        self.filename = filename
        if flag != 'n' and os.access(filename, os.R_OK):
            fileobj = open(filename, 'rb' if format=='pickle' else 'r')
            with fileobj:
                self.load(fileobj)
        dict.__init__(self, *args, **kwds)

    def sync(self):
        'Write dict to disk'
        if self.flag == 'r':
            return
        filename = self.filename
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.format=='pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            raise
        finally:
            fileobj.close()
        shutil.move(tempname, self.filename)    # atomic commit
        if self.mode is not None:
            os.chmod(self.filename, self.mode)

    def close(self):
        self.sync()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def dump(self, fileobj):
        if self.format == 'csv':
            csv.writer(fileobj).writerows(self.items())
        elif self.format == 'json':
            json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))

    def load(self, fileobj):
        # try formats from most restrictive to least restrictive
        for loader in (pickle.load, json.load, csv.reader):
            fileobj.seek(0)
            try:
                return self.update(loader(fileobj))
            except Exception:
                pass
        raise ValueError('File not in a supported format')
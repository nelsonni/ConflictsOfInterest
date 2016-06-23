class Conflict:
    def __init__(self, file_conflicts):
        self.file_conflicts = file_conflicts

    def addFileConflict(self, file_conflict):
        self.file_conflicts.append(file_conflict)
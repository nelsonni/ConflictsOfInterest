class FileConflict:
    def __init__(self, filename, line_conflicts):
        self.filename = filename
        self.line_conflicts = line_conflicts

    def addLineConflict(self, line_conflict):
        self.line_conflicts.append(line_conflict)
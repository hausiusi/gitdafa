class Change:
    def __init__(self, file_name:str = None, added:str = None, deleted:str = None):
        self.file = file_name
        self.added = added
        self.deleted = deleted

    def __str__(self):
        return f"File: {self.file}, "  + \
            f"Added: {self.added}, " + \
            f"Deleted: {self.deleted}"

    def __repr__(self):
        return f"'File': '{self.file}'"

class Change:
    """
    Model, to reflect file change properties.
    
    Parameters
    ----------
    file_name : str, optional
    added : str, optional
    deleted : str, optional    
    
    Attributes
    ----------
    self.file : str
        File name
    self.added : int
    self.deleted : int

    """
    def __init__(self,
                 file_name: str = None,
                 added: int = 0,
                 deleted: int = 0):
        self.file = file_name
        self.added = added
        self.deleted = deleted

    def __eq__(self, item):
        if (item.added == self.added and item.deleted == self.deleted
                and item.file == self.file):
            return True
        else:
            return False

    def __str__(self):
        return f"File: {self.file}, "  + \
            f"Added: {self.added}, " + \
            f"Deleted: {self.deleted}"

    def __repr__(self):
        return f"'File': '{self.file}'"

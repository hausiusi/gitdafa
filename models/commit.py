class Commit:
    def __init__(self,
                 commit_id: str,
                 author: str = None,
                 date=None,
                 message: str = None):
        self._id = commit_id
        self.author = author
        self.date = date
        self.message = message
        self.changes = []

    def __str__(self):
        return f"Author: {self.author}, " +\
            f"Date: {self.date}, " +\
            f"Message: {self.message}"

    def __repr__(self):
        return f"'author': {self.author.email if self.author else 'None'}, " + \
            f"'date': {self.date}"

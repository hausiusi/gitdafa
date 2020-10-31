
class Cmd:
    """String constants for a git command"""

    LOG = "git log --pretty=oneline"
    SHOW = "git show --stat {commit}"
    SHORTLOG = "git shortlog -s"
    LOG_STAT = "git log --stat"
    LOG_NUMSTAT = "git log --numstat"

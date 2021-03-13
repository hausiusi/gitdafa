class Cmd:
    """String constants for a git command"""

    LOG = 'git log --pretty=oneline'
    SHOW = 'git show --stat {commit}'
    SHORTLOG = 'git shortlog -s'
    LOG_STAT = 'git log --stat'
    LOG_NUMSTAT = 'git log --numstat'
    NUMSTAT_OUTPUT_FORMAT = '"commit %H%nAuthor: %an <%ae>%nDate: %ad%n%n%x09%s%n"'
    LOG_NUMSTAT_SKIP_X_GET_Y_FMT = 'git log --numstat --skip=%d -%d --pretty=format:%s'
    LOG_NUMSTAT_SKIP_X_GET_Y = 'git log --numstat --skip=%d -%d'
    TAGS = 'git tag -l'
    REV_PARSE = 'git rev-parse %s^{}'
    SHA_LIST = 'git log --pretty=format:%H --no-patch'
    SHA_LIST_REVERSED = SHA_LIST + ' --reverse'
    BRANCH_TAG_CONTAINS = 'git branch -a --contains tags/%s'
    CURRENT_BRANCH = 'git rev-parse --abbrev-ref HEAD'
    COMMIT_COUNT_ALL = 'git rev-list --all --count'
    COMMIT_COUNT_BRANCH = 'git rev-list --count HEAD'

# constants related to cses parser

# form constants
CSES_USERNAME_FORM_NAME = "nick"
CSES_PASSWORD_FORM_NAME = "pass"
CSES_CSRF_TOKEN_FORM_NAME = "csrf_token"

# table attribute constants
CSES_TABLE_CLASS = "wide"
CSES_TABLE_SUBMISSION_COL = "submission"
CSES_TABLE_VERDICT_COL = "result"
CSES_TABLE_TIMESTAMP_COL = "time"
CSES_TABLE_CODE_LANG_COL = "lang"
CSES_TABLE_CODE_TIME_COL = "code time"
CSES_TABLE_CODE_SIZE_COL = "code size"

# other page constants
CSES_ACCOUNT_ANCHOR_CLASS = "account"
CSES_AC_PROBLEM_CLASS = "task-score icon full"
CSES_AC_PROBLEM_TITLE_CLASS = "title-block"
CSES_PAGE_SPAN_CLASS = "pager wide"
CSES_NEXT_PAGE_CLASS = "next"
CSES_PREV_PAGE_CLASS = "prev"
CSES_CODE_LINK_CONTENT_CLASS = "prettyprint linenums resize-horizontal"

# yaml constants
CSES_YAML_REL_PATH = "../../files/cses.yaml"
CSES_USERNAME_YAML_NAME = "username"
CSES_PASSWORD_YAML_NAME = "password"

# file constants
CSES_REL_OUT_DIR = "../../.out"

# url constants
CSES_BASE_URL = "https://cses.fi"
CSES_LOGIN_URL = "https://cses.fi/login"
CSES_PROBLEMS_URL = "https://cses.fi/problemset"
CSES_PROBLEM_RESULTS_URL = "https://cses.fi/problemset/view"

# extension mappings
EXTENSION_MAPPING = {
    "java": "java",
    "c++": "cpp",
    "python": "py"
}

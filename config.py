# crawl and refresh config
MAX_CRAWL_COUNT_TOTAL = 15
MAX_CRAWL_COUNT_NEW = 15
REFRESH_UPDATE_REPO_DAYS = 30
REFRESH_UPDATE_USER_DAYS = 30
REFRESH_UPDATE_USER_REPOS_DAYS = 3
REFRESH_CRAWL_DAYS = 30

# search defaults
DEFAULT_COUNT = 15

# URLs, hostnames, and endpoints
DB_URI = "postgresql:///git_data"
TEST_DB_URI = "postgresql:///git_test"
OAUTH_SCOPE = "user user:follow read:user public_repo"
ENDPOINT = "https://api.github.com"
GITHUB_AUTH_REQUEST_CODE_URL = "https://github.com/login/oauth/authorize"
GITHUB_AUTH_REQUEST_TOKEN_URL = "https://github.com/login/oauth/access_token"
AUTHENTICATED_USER_PATH = "/user"

CLIENT_ID = "2adef54000501a55be8c"

# crawl and refresh config
MAX_CRAWL_COUNT_TOTAL = 50
MAX_CRAWL_COUNT_NEW = 50
REFRESH_UPDATE_REPO_DAYS = 7
REFRESH_UPDATE_USER_DAYS = 7
REFRESH_UPDATE_USER_REPOS_DAYS = 1
REFRESH_CRAWL_DAYS = 30

# search defaults
DEFAULT_COUNT = 12

# URLs, hostnames, and endpoints
DB_URI = "postgres:///git_data"
AUTH_CALLBACK_URL = "http://127.0.0.1:5000/auth"
OAUTH_SCOPE = "user user:follow read:user public_repo"
ENDPOINT = "https://api.github.com"
GITHUB_AUTH_REQUEST_CODE_URL = "https://github.com/login/oauth/authorize"
GITHUB_AUTH_REQUEST_TOKEN_URL = "https://github.com/login/oauth/access_token"
AUTHENTICATED_USER_PATH = "/user"

CLIENT_ID = "2adef54000501a55be8c"

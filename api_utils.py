import os
import github
import config

if not os.environ.get("CLIENT_ID"):
    import secrets2
    print(os.environ.get("CLIENT_ID"))

def get_auth_api(access_token):
    print(f"Access token: {access_token[:5]}...")
    return github.Github(access_token,
                         client_id=config.CLIENT_ID,
                         client_secret=os.environ.get("CLIENT_SECRET"))


def get_api():
    access_token = os.environ.get("PERSONAL_ACCESS_TOKEN")
    return get_auth_api(access_token)


def get_repo_from_api(repo_id):
    """Given repo id, return pygithub Repository object."""
    return g.get_repo(repo_id)


def get_user_from_api(login):
    """Given user login, return pygithub NamedUser object."""
    return g.get_user(login=login)


def get_user_repos_from_api(user):
    """Get all repos owned by user from api."""
    return user.get_repos()


def get_starred_repos_from_api(user):
    """Get all repos starred by user from api."""
    return user.get_starred()


def get_stargazers_from_api(repo):
    """Get all users that have starred this repo from api."""
    return repo.get_stargazers()


def get_languages_from_api(repo):
    """Given a repository, get list of languages for that repo."""
    return repo.get_languages()


g = get_api()

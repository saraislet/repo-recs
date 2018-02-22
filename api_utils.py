import github
import secrets


def get_auth_api(access_token):
    return github.Github(access_token,
                         client_id=secrets.client_id,
                         client_secret=secrets.client_secret)

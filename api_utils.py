import os
import github

def get_auth_api(access_token):
    return github.Github(access_token,
                         client_id=os.environ.get("CLIENT_ID"),
                         client_secret=os.environ.get("CLIENT_SECRET"))

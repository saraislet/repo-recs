# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 16:32:46 2018

@author: Sarai
"""

import os
from github import Github
import secrets

token = secrets.personal_access_token
client_id = secrets.client_id
client_secret = secrets.client_secret

g = Github(token, client_id=client_id, client_secret=client_secret)

for repo in g.get_user().get_repos():
    print(repo.name)

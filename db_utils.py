from flask import Flask
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
import utils


def get_ratings_from_db():
    """Return list of ratings of repos by users."""
    ratings = Stargazer.query.all()
    return [ [rating.user_id, rating.repo_id, 1] for rating in ratings ]

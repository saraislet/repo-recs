from flask import Flask
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
import utils


def get_ratings_from_db():
    """Return list of ratings of repos by users."""
    ratings = Stargazer.query.all()
    return [ [rating.user_id, rating.repo_id, 1] for rating in ratings ]

def filter_stars_from_repo_ids(repo_ids, user_id):
    """Remove any repo_ids that are starred by the user and return remaining."""
    stars = Stargazer.query.filter_by(user_id=user_id)
    stars = stars.with_entities(Stargazer.repo_id).all()
    star_ids = [star.repo_id for star in stars]

    return [repo_id for repo_id in repo_ids if repo_id not in star_ids]

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
    """Remove repo_ids starred by the user and return remaining."""
    stars = Stargazer.query.filter_by(user_id=user_id)
    stars = stars.with_entities(Stargazer.repo_id).all()
    star_ids = [star.repo_id for star in stars]

    return [repo_id for repo_id in repo_ids if repo_id not in star_ids]

def add_stargazer(repo_id, user_id):
    """Add stargazer to database."""
    this_star = Stargazer(repo_id=repo_id, user_id=user_id)
    db.session.add(this_star)
    db.session.commit()
    print("Added star to database: repo {}, user {}."
          .format(repo_id, user_id))

def remove_stargazer(repo_id, user_id):
    """Remove stargazer from database."""
    this_star = Stargazer.query.filter_by(repo_id=repo_id,
                                          user_id=user_id).first()
    db.session.delete(this_star)
    db.session.commit()
    print("Removed star from database: repo {}, user {}."
          .format(repo_id, user_id))


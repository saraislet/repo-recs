import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds
from flask import Flask
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
import utils, db_utils


def build_ratings_dataframe():
    """Build and return pandas DataFrame of all ratings by users of repos."""

    ratings = db_utils.get_ratings_from_db()
    ratings_df = pd.DataFrame(ratings, columns = ["user_id", "repo_id", "Rating"], dtype = int)
    R_df = ratings_df.pivot(index="user_id", columns = "repo_id", values = "Rating").fillna(0)

    return R_df


def build_repo_predictions_matrix():
    """Build matrix of predictions for ratings by users of repos."""

    # Build a matrix of binary ratings by users of repos.
    R_df = build_ratings_dataframe()
    R = R_df.as_matrix()

    # Normalize the matrix by subtracting off each users' mean.
    user_ratings_mean = np.mean(R, axis = 1)
    R_demeaned = R - user_ratings_mean.reshape(-1, 1)

    U, sigma, Vt = svds(R_demeaned, k = 50)
    sigma = np.diag(sigma)
    predictions_matrix = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    
    return pd.DataFrame(predictions_matrix, columns = R_df.columns, index = R_df.index)


def get_repo_suggestions(user_id):
    """Given a user_id, return list of suggested repo_ids."""

    predictions_df = build_repo_predictions_matrix()
    
    #FIXME: Why doesn't predictions_df < 1 work?
    suggestions = (predictions_df[predictions_df < 0.99999]
                                 .loc[user_id]
                                 .sort_values(ascending=False)
                                 .index.tolist())
    #TODO: Can we have Pandas interpret index items as a Python int instead of a numpy object?
    return [ int(n) for n in suggestions ]


def compare_recs(user_id1, user_id2, num_recs=20, preds=[]):
    if len(preds) != num_recs:
        preds = set(get_repo_suggestions(user_id1)[:num_recs])
    preds2 = set(get_repo_suggestions(user_id2)[:num_recs])

    overlap = preds.intersection(preds2)

    return len(overlap)/num_recs


def get_comparisons(user_id, num_users=20, num_recs=20):
    users = User.query.limit(num_users).all()
    preds1 = set(get_repo_suggestions(user_id)[:num_recs])
    return [ compare_recs(user_id,
                          user.user_id, 
                          num_recs=num_recs, 
                          preds=preds1) for user in users ]



if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(db_uri))

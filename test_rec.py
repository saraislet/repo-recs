import unittest
from flask import Flask
import config, rec
from model import (Repo, User, Follower, Account,
                   Stargazer, Dislike,
                   Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
from test_model import example_data

app = Flask(__name__)


class TestRec(unittest.TestCase):
    """Test rec functions that use the DB."""

    def setUp(self):
        """Connect to database, create tables, generate test data."""

        self.client = app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, config.TEST_DB_URI)
        db.drop_all()
        db.create_all()
        example_data()
        # update_pkey_seqs.update_pkey_seqs()

    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_build_ratings_dataframe(self):

        M = [[1, 0], [1, 1]]
        R = rec.build_ratings_dataframe().as_matrix().tolist()
        self.assertEqual(R, M)

    def test_build_repo_predictions_matrix(self):
      
        M = [[1, 0], [1, 1]]
        preds = rec.build_repo_predictions_matrix().as_matrix().tolist()
        self.assertEqual(preds, M)

    def test_get_repo_suggestions(self):
        
        M = [2, 1]
        preds = rec.get_repo_suggestions(2)
        self.assertEqual(preds, M)

    def test_compare_recs(self):
        
        ratio = rec.compare_recs(2, 3)
        self.assertEqual(ratio, 1)


if __name__ == "__main__":
    unittest.main()

import unittest
import datetime, json
from flask import Flask
import config, db_utils, update_pkey_seqs
from model import (Repo, User, Follower, Account,
                   Stargazer, Dislike,
                   Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
from test_model import example_data

app = Flask(__name__)


class TestDB(unittest.TestCase):
    """Test utils functions that use the DB."""

    def setUp(self):
        """Connect to database, create tables, generate test data."""

        self.client = app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, config.TEST_DB_URI)
        db.drop_all()
        db.create_all()
        example_data()
        update_pkey_seqs.update_pkey_seqs()

    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_get_ratings(self):

        ratings = [[2, 1, 1],
                   [3, 1, 1],
                   [3, 2, 1]]
        self.assertEqual(ratings, db_utils.get_ratings_from_db())

    def test_get_json_from_repos(self):

        repo_dict = [{"repo_id": 1,
                      "description": "A Python repository",
                      "name": "python-repo",
                      "owner_login": "jhacks",
                      "stargazers_count": 2,
                      "url": "https://github.com/jhacks/python-repo",
                      "langs": [{"language_id": 1,
                                 "language_name": "python",
                                 "language_bytes": 5000},
                                {"language_id": 2,
                                 "language_name": "c",
                                 "language_bytes": 100}]
                    }]
        repo_json = json.dumps(repo_dict)
        repo = Repo.query.get(1)

        self.assertEqual(repo_json, db_utils.get_json_from_repos([repo]))

    def test_filter_stars_pass(self):
        repo_ids = [2]
        user_id = 2
        filtered_ids = db_utils.filter_stars_from_repo_ids(repo_ids, user_id)

        self.assertEqual([2], filtered_ids)

    def test_filter_stars_removal(self):
        repo_ids = [1]
        user_id = 2
        filtered_ids = db_utils.filter_stars_from_repo_ids(repo_ids, user_id)

        self.assertEqual([], filtered_ids)

    def test_is_last_crawled_in_user_good_true(self):
        self.assertTrue(db_utils.is_last_crawled_in_user_good(1, 2))

    def test_is_last_crawled_in_user_good_false_depth(self):
        self.assertFalse(db_utils.is_last_crawled_in_user_good(1, 3))

    def test_is_last_crawled_in_user_good_false_crawled_since(self):
        old_date = datetime.datetime.now() + datetime.timedelta(weeks = 2)
        self.assertFalse(db_utils.is_last_crawled_in_user_good(1, 2, old_date))

    def test_is_last_crawled_in_user_good_false_old_crawl(self):
        self.assertFalse(db_utils.is_last_crawled_in_user_good(2, 2))

    def test_is_last_crawled_in_repo_good_true(self):
        self.assertTrue(db_utils.is_last_crawled_in_repo_good(1, 2))

    def test_is_last_crawled_in_repo_good_false_depth(self):
        self.assertFalse(db_utils.is_last_crawled_in_repo_good(1, 3))

    def test_is_last_crawled_in_repo_good_false_crawled_since(self):
        old_date = datetime.datetime.now() + datetime.timedelta(weeks = 2)
        self.assertFalse(db_utils.is_last_crawled_in_repo_good(1, 2, old_date))

    def test_is_last_crawled_in_repo_good_false_old_crawl(self):
        self.assertFalse(db_utils.is_last_crawled_in_repo_good(2, 2))


class TestDB_AddRemove(unittest.TestCase):
    """Test utils functions that use the DB."""

    def setUp(self):
        """Connect to database, create tables, generate test data."""

        self.client = app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, config.TEST_DB_URI)
        db.drop_all()
        db.create_all()
        example_data()
        update_pkey_seqs.update_pkey_seqs()

    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_add_stargazer(self):

        self.assertEqual(0, Stargazer.query.filter_by(repo_id=2, user_id=2).count())
        db_utils.add_stargazer(2, 2)
        self.assertEqual(1, Stargazer.query.filter_by(repo_id=2, user_id=2).count())

    def test_add_stargazer_duplicate(self):

        db_utils.add_stargazer(2, 2)
        db_utils.add_stargazer(2, 2)
        self.assertEqual(1, Stargazer.query.filter_by(repo_id=2, user_id=2).count())

    def test_remove_stargazer(self):

        self.assertEqual(1, Stargazer.query.filter_by(repo_id=2, user_id=3).count())
        db_utils.remove_stargazer(2, 3)
        self.assertEqual(0, Stargazer.query.filter_by(repo_id=2, user_id=3).count())

    def test_remove_stargazer_unknown(self):

        db_utils.remove_stargazer(5, 3)
        self.assertEqual(0, Stargazer.query.filter_by(repo_id=5, user_id=3).count())

    def test_add_dislike(self):

        self.assertEqual(0, Dislike.query.filter_by(repo_id=2, user_id=3).count())
        db_utils.add_dislike(2, 3)
        self.assertEqual(1, Dislike.query.filter_by(repo_id=2, user_id=3).count())

    def test_add_dislike_duplicate(self):

        db_utils.add_dislike(2, 3)
        db_utils.add_dislike(2, 3)
        self.assertEqual(1, Dislike.query.filter_by(repo_id=2, user_id=3).count())

    def test_remove_dislike(self):

        self.assertEqual(1, Dislike.query.filter_by(repo_id=2, user_id=2).count())
        db_utils.remove_dislike(2, 2)
        self.assertEqual(0, Dislike.query.filter_by(repo_id=2, user_id=2).count())

    def test_remove_dislike_unknown(self):

        db_utils.remove_dislike(5, 3)
        self.assertEqual(0, Dislike.query.filter_by(repo_id=5, user_id=3).count())


if __name__ == "__main__":
    unittest.main()

import unittest
from flask import session
from server import app
from model import (Repo, User, Follower, Account,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
from test_model import test_db_uri, example_data


class ServerTests(unittest.TestCase):
    """Test server functions that do not use the DB."""

    def setUp(self):
        """Connect to database, create tables, generate test data."""

        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_homepage(self):
        result = self.client.get("/").data.decode("utf-8")
        print(type(result))
        self.assertIn("Welcome!", result)

    def test_no_logout(self):
        result = self.client.get("/").data.decode("utf-8")
        self.assertNotIn("Logout", result)
        self.assertNotIn("Recommendations", result)
        self.assertIn("Login", result)


class LoginLogoutTests(unittest.TestCase):
    """Test server session when logged in and logging out."""

    def setUp(self):
        """Connect to database, create tables, generate test data."""

        self.client = app.test_client()
        app.config["TESTING"] = True
        connect_to_db(app, test_db_uri)
        db.drop_all()
        db.create_all()
        example_data()

    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_profile(self):
        """Test showing profile when user is logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 1

            result = self.client.get("/me").data.decode("utf-8")
            self.assertIn("Jane", result)
            self.assertIn("jhacks", result)
            self.assertIn("python-repo", result)

    def test_no_login(self):
        """Test conditional navbar items when user is logged in."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 1

        result = self.client.get("/").data.decode("utf-8")
        self.assertIn("Logout", result)
        self.assertIn("Recommendations", result)
        self.assertNotIn("Login", result)

    #TODO: Test login path with mocking?

    def test_logout(self):
        """Test logout route."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = "1"

            result = self.client.get("/logout", follow_redirects=True).data.decode("utf-8")

            self.assertNotIn("user_id", session)
            self.assertNotIn("Logout", result)
            self.assertNotIn("Recommendations", result)
            self.assertIn("Login", result)

if __name__ == "__main__":
    unittest.main()

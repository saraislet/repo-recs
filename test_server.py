from urllib.request import urlopen
import unittest
from flask import Flask, session
# import flask_testing
from server import app
from model import (Repo, User, Follower, Account,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
from test_model import test_db_uri, example_data


# class LiveServerTests(flask_testing.LiveServerTestCase):
#     """Test live server functions that do not use the DB."""

#     def create_app(self):
#         """Create app for flask_testing."""
#         app = Flask(__name__)
#         app.config['TESTING'] = True
#         return app

#     def setUp(self):
#         """Connect to database, create tables, generate test data."""
#         self.client = app.test_client()
#         app.config["TESTING"] = True

#     def test_server(self):
#         response = urlopen(self.get_server_url())
#         self.assertEqual(response.code, 200)


class ServerTests(unittest.TestCase):
    """Test server functions that do not use the DB."""

    def create_app(self):
        """Create app for flask testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

    def setUp(self):
        """Connect to database, create tables, generate test data."""
        self.client = app.test_client()
        app.config["TESTING"] = True

    def test_homepage(self):
        """Test homepage when user is logged out."""
        result = self.client.get("/").data.decode("utf-8")
        self.assertIn("Welcome!", result)

    def test_about(self):
        """Test about when user is logged out."""

        with self.client as c:
            result = self.client.get("/about")
            self.assertEqual(result.status_code, 302)

            with c.session_transaction() as sess:
                flash = dict(sess["_flashes"]).get("message")
                self.assertIn("Oops!", flash)

    def test_logged_out_route_auth(self):
        """Test auth redirect when user is logged out and not sending code&state."""
        with self.client as c:
            result = self.client.get("/about")
            self.assertEqual(result.status_code, 302)

            with c.session_transaction() as sess:
                flash = dict(sess["_flashes"]).get("message")
                self.assertIn("Oops!", flash)

    def test_no_logout(self):
        """Test conditional navbar items when user is logged out."""
        result = self.client.get("/").data.decode("utf-8")
        self.assertNotIn("Logout", result)
        self.assertNotIn("Recommendations", result)
        self.assertIn("Login", result)

    def test_logged_out_route_me(self):
        """Test route redirect when user is logged out."""
        result = self.client.get("/me")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_logout(self):
        """Test route redirect when user is logged out."""
        result = self.client.get("/logout")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_login(self):
        """Test route redirect when user is logged out."""
        result = self.client.get("/login")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_recs(self):
        """Test route redirect when user is logged out."""
        result = self.client.get("/recs")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_get_recs(self):
        """Test route redirect when user is logged out."""
        result = self.client.get("/get_repo_recs")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_add_star(self):
        """Test route redirect when user is logged out."""
        result = self.client.post("/add_star")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_remove_star(self):
        """Test route redirect when user is logged out."""
        result = self.client.post("/remove_star")
        self.assertEqual(result.status_code, 302)

    def test_logged_out_route_check_star(self):
        """Test route redirect when user is logged out."""
        result = self.client.post("/check_star")
        self.assertEqual(result.status_code, 302)


class LoginLogoutTests(unittest.TestCase):
    """Test server session when logged in and logging out."""

    def create_app(self):
        """Create app for flask testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

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

    def test_login_redirect(self):
        """Test conditional navbar items when user is logged in."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 1

        result = self.client.get("/login")
        self.assertEqual(result.status_code, 302)

    def test_auth_redirect(self):
        """Test conditional navbar items when user is logged in."""
        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 1

        result = self.client.get("/auth")
        self.assertEqual(result.status_code, 302)

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


class TestRoutesWithDB(unittest.TestCase):
    """Test server session when logged in and logging out."""

    def create_app(self):
        """Create app for flask testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app

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

    def test_user_profile_success(self):
        """Test showing another user profile when user is logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 2

            result = self.client.get("/user?login=jhacks").data.decode("utf-8")
            self.assertIn("Jane", result)
            self.assertIn("jhacks", result)
            self.assertIn("python-repo", result)

    def test_user_profile_id_success(self):
        """Test showing another user profile when user is logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 2

            result = self.client.get("/user?user_id=1").data.decode("utf-8")
            self.assertIn("Jane", result)
            self.assertIn("jhacks", result)
            self.assertIn("python-repo", result)

    def test_user_profile_casing_success(self):
        """Test showing another user profile when user is logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 2

            result = self.client.get("/user?login=jHACKS").data.decode("utf-8")
            self.assertIn("Jane", result)
            self.assertIn("jhacks", result)
            self.assertIn("python-repo", result)

    def test_user_profile_failure(self):
        """Test showing a profile request failure when user is logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 2

            result = self.client.get("/user?login=null")

            with c.session_transaction() as sess:
                flash = dict(sess["_flashes"]).get("message")
                self.assertIn("Unable to find user", flash)
            self.assertEqual(result.status_code, 302)

    def test_user_profile_null_failure(self):
        """Test showing a profile request failure when user is logged in."""

        with self.client as c:
            with c.session_transaction() as sess:
                sess["user_id"] = 2

            result = self.client.get("/user")

            with c.session_transaction() as sess:
                flash = dict(sess["_flashes"]).get("message")
                self.assertIn("Unable to find user", flash)
            self.assertEqual(result.status_code, 302)

    # def test_get_json_from_repos(self):
    #     """Test getting json of repos."""
    #     result = self.client.get("/get_repo_recs").data.decode("utf-8")
    #     self.assertEquals(result.json, dict(success=True))


if __name__ == "__main__":
    unittest.main()

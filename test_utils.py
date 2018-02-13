import unittest, datetime
from flask import Flask
import github
import utils, update_pkey_seqs
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
from test_model import test_db_uri, example_data

app = Flask(__name__)

class TestDB_add_update(unittest.TestCase):
    """Test utils functions that use the DB."""

    def setUp(self):
        """Connect to database, create tables, generate test data."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, test_db_uri)
        db.drop_all()
        db.create_all()
        example_data()
        update_pkey_seqs.update_pkey_seqs()

    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_add_lang_new(self):
        lang = "Haskell"
        utils.add_lang(lang)

        self.assertEqual(1, Language.query.filter_by(language_name=lang.lower()).count())

    def test_add_lang_existing(self):
        lang = "c"
        utils.add_lang(lang)

        self.assertEqual(1, Language.query.filter_by(language_name=lang).count())

    def test_add_lang_casing(self):
        lang = "C"
        utils.add_lang(lang)

        self.assertEqual(0, Language.query.filter_by(language_name=lang).count())
        self.assertEqual(1, Language.query.filter_by(language_name=lang.lower()).count())

    def test_add_repo_lang_new(self):
        repo_id = 1
        lang = "Haskell"
        num = 512
        utils.add_lang(lang)
        utils.add_repo_lang(repo_id, lang, num)

        this_lang = Language.query.filter_by(language_name=lang.lower()).one()
        this_repo_lang = RepoLanguage.query.filter_by(repo_id=repo_id,
                                                      language_id=this_lang.language_id).one()

        self.assertEqual(512, this_repo_lang.language_bytes)

    def test_add_repo_lang_existing(self):
        repo_id = 1
        lang = "c"
        num = 1024
        utils.add_lang(lang)
        utils.add_repo_lang(repo_id, lang, num)

        this_lang = Language.query.filter_by(language_name=lang.lower()).one()
        this_repo_lang = RepoLanguage.query.filter_by(repo_id=repo_id,
                                                      language_id=this_lang.language_id).one()

        self.assertEqual(1024, this_repo_lang.language_bytes)

    def test_set_last_crawled_in_repo(self):
        this_repo = Repo.query.get(1)
        now = datetime.datetime.now()
        utils.set_last_crawled_in_repo(this_repo.repo_id, now) 

        self.assertEqual(now, Repo.query.get(1).last_crawled)

    def test_set_last_crawled_in_user(self):
        this_user = User.query.get(1)
        now = datetime.datetime.now()
        utils.set_last_crawled_in_user(this_user.user_id, now) 

        self.assertEqual(now, User.query.get(1).last_crawled)


class TestRepoTypes(unittest.TestCase):

    def setUp(self):
        """Connect to database, create tables."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, test_db_uri)
        db.drop_all()
        db.create_all()
        # example_data()
        update_pkey_seqs.update_pkey_seqs()

        self.repo = Repo(repo_id="2",
                         name="Haskellyton",
                         description="A Halloween repository",
                         owner_id="1")

        repo_attributes = {"id": "2",
                           "name": "Haskellyton",
                           "full_name": "Haskellyton",
                           "description": "A Halloween repository",
                           "owner_id": "1"}

        self.py_repo = github.Repository.Repository(requester="",
                                                    headers="",
                                                    attributes=repo_attributes,
                                                    completed="")
        py_repo = self.py_repo

        # Don't call the Github API: just return self.py_repo when this is called.
        github.Github.get_repo = lambda self, num: py_repo


    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_get_repo_object_from_input_int(self):
        
        self.assertEqual(self.py_repo, utils.get_repo_object_from_input(2))

    def test_get_repo_object_from_input_model(self):

        self.assertEqual(self.py_repo, utils.get_repo_object_from_input(self.repo))

    def test_get_repo_object_from_input_pygithub_object(self):

        self.assertEqual(self.py_repo, utils.get_repo_object_from_input(self.py_repo))

    def test_get_repo_object_from_input_fail(self):

        self.assertRaises(TypeError, utils.get_repo_object_from_input, [])


class TestUserTypes(unittest.TestCase):

    def setUp(self):
        """Connect to database, create tables."""

        self.client = app.test_client()
        app.config['TESTING'] = True
        connect_to_db(app, test_db_uri)
        db.drop_all()
        db.create_all()
        # example_data()
        update_pkey_seqs.update_pkey_seqs()

        self.user = User(user_id="4",
                         name="Balloonicorn Doe",
                         login="balloonicorn")
        db.session.add(self.user)
        db.session.commit()

        user_attributes = {"id": "4",
                           "name": "Balloonicorn Doe",
                           "login": "balloonicorn"}

        self.py_user = github.NamedUser.NamedUser(requester="",
                                                  headers="",
                                                  attributes=user_attributes,
                                                  completed="")
        user = self.user
        py_user = self.py_user

        # don't call the github api: just return self.py_repo when this is called.
        github.Github.get_user = lambda self, login: py_user
        # User.query.get = lambda num: user
        # import pdb; pdb.set_trace()


    def tearDown(self):
        """Close session, drop db."""
        db.session.close()
        db.drop_all()

    def test_get_user_object_from_input_int(self):
        
        self.assertEqual(self.py_user, utils.get_user_object_from_input(4))

    def test_get_user_object_from_input_str(self):
        
        self.assertEqual(self.py_user, utils.get_user_object_from_input("balloonicorn"))

    def test_get_user_object_from_input_model(self):

        self.assertEqual(self.py_user, utils.get_user_object_from_input(self.user))

    def test_get_user_object_from_input_pygithub_object(self):

        self.assertEqual(self.py_user, utils.get_user_object_from_input(self.py_user))

    def test_get_user_object_from_input_fail(self):

        self.assertRaises(TypeError, utils.get_user_object_from_input, [])


if __name__ == '__main__':
    unittest.main()

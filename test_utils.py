import unittest
from flask import Flask
import utils, update_pkey_seqs
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
from test_model import test_db_uri, example_data

app = Flask(__name__)

class TestDB(unittest.TestCase):
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

        self.assertEqual(1, Language.query.filter_by(language_name=lang).count())

    def test_add_lang_existing(self):
        lang = "c"
        utils.add_lang(lang)

        self.assertEqual(1, Language.query.filter_by(language_name=lang).count())

    def test_add_repo_lang_new(self):
        repo_id = 1
        lang = "Haskell"
        num = 512
        utils.add_lang(lang)
        utils.add_repo_lang(repo_id, lang, num)

        this_lang = Language.query.filter_by(language_name=lang).one()
        this_repo_lang = RepoLanguage.query.filter_by(repo_id=repo_id,
                                                      language_id=this_lang.language_id).one()

        self.assertEqual(512, this_repo_lang.language_bytes)

    def test_add_repo_lang_existing(self):
        repo_id = 1
        lang = "c"
        num = 1024
        utils.add_lang(lang)
        utils.add_repo_lang(repo_id, lang, num)

        this_lang = Language.query.filter_by(language_name=lang).one()
        this_repo_lang = RepoLanguage.query.filter_by(repo_id=repo_id,
                                                      language_id=this_lang.language_id).one()

        self.assertEqual(1024, this_repo_lang.language_bytes)


if __name__ == '__main__':
    unittest.main()

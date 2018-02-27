import datetime
from flask import Flask
import config
from model import (Repo, User, Follower, Account,
                   Stargazer, Dislike,
                   Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)


def example_data():
    """Create example data for the test database."""
    Stargazer.query.delete()
    Watcher.query.delete()
    Follower.query.delete()
    Contributor.query.delete()
    RepoLanguage.query.delete()
    Language.query.delete()
    Repo.query.delete()
    Account.query.delete()
    User.query.delete()

    jane = User(user_id="1",
                      login="jhacks",
                      name="Jane",
                      last_crawled=datetime.datetime.now(),
                      last_crawled_depth=2)
    alex = User(user_id="2",
                      login="ajax",
                      name="Alex")
    kelly = User(user_id="3",
                      login="kells",
                      name="Kelly")
    db.session.add_all([jane, alex, kelly])
    db.session.commit()

    jane_account = Account(user_id="1",
                           access_token="abc123")
    db.session.add(jane_account)
    db.session.commit()

    py_repo = Repo(repo_id="1",
                   name="python-repo",
                   description="A Python repository",
                   owner_id="1",
                   last_crawled=datetime.datetime.now(),
                   last_crawled_depth=2,
                   url="https://github.com/jhacks/python-repo",
                   stargazers_count=2)
    js_repo = Repo(repo_id="2",
                   name="js-repo",
                   description="A Javascript repository",
                   owner_id="1",
                   last_crawled=datetime.datetime.now(),
                   last_crawled_depth=1,
                   url="https://github.com/jhacks/js-repo",
                   stargazers_count=1)
    db.session.add_all([py_repo, js_repo])
    db.session.commit()

    astar = Stargazer(repo_id="1", user_id="2")
    kstar = Stargazer(repo_id="1", user_id="3")
    kstar_js = Stargazer(repo_id="2", user_id="3")
    a_dislike_js = Dislike(repo_id="2", user_id="3")
    db.session.add_all([astar, kstar, kstar_js, a_dislike_js])
    db.session.commit()

    kwatch = Watcher(repo_id="1", user_id="3")
    a_j_follow = Follower(user_id="1", follower_id="2")
    k_j_follow = Follower(user_id="1", follower_id="3")
    j_a_follow = Follower(user_id="2", follower_id="1")
    db.session.add_all([kwatch, a_j_follow, k_j_follow, j_a_follow])
    db.session.commit()

    jcon = Contributor(repo_id="1", user_id="1")
    kcon = Contributor(repo_id="1", user_id="3")
    db.session.add_all([jcon, kcon])
    db.session.commit()

    # python = Topic(topic_id="1", topic_name="python")
    # api = Topic(topic_id="2", topic_name="api")
    # db.session.add_all([python, api])
    # db.session.commit()

    # py_rep1 = RepoTopic(topic_id="1", repo_id="1")
    # api_rep1 = RepoTopic(topic_id="2", repo_id="1")
    # db.session.add_all([py_rep1, api_rep1])
    # db.session.commit()

    py_lang = Language(language_id="1", language_name="python")
    c_lang = Language(language_id="2", language_name="c")
    db.session.add_all([py_lang, c_lang])
    db.session.commit()

    py_lang_rep1 = RepoLanguage(language_id="1", repo_id="1", language_bytes=5000)
    c_lang_rep1 = RepoLanguage(language_id="2", repo_id="1", language_bytes=100)
    db.session.add_all([py_lang_rep1, c_lang_rep1])
    db.session.commit()

    # print("Created test data.")


if __name__ == "__main__":  # pragma: no cover
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app, uri=config.TEST_DB_URI)
    print("Connected to DB {}.".format(config.TEST_DB_URI))

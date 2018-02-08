import os, datetime
from github import Github
from progress.bar import ShadyBar
from progress.spinner import Spinner
import secrets
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   # Topic, RepoTopic,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
# TODO: try Tenacity library

token = secrets.personal_access_token
client_id = secrets.client_id
client_secret = secrets.client_secret

g = Github(token, client_id=client_id, client_secret=client_secret)
progress_bar_suffix = "%(index)d/%(max)d, estimated %(eta)d seconds remaining."
spinner_suffix = "%(index)d added, avg %(avg)ds each, %(elapsed)d time elapsed."

# for repo in g.get_user().get_repos():
#     print(repo.name)

def add_repo(repo):
    """Query API, and update repo details in db."""

    if is_repo_in_db(repo):
        return

    owner = repo.owner
    owner_id = owner.id
    # Must create User for owner before commiting Repo to db.
    add_user(owner)
    
    this_repo = Repo(repo_id=repo.id,
                     name=repo.name,
                     description=repo.description,
                     owner_id=owner.id,
                     created_at=repo.created_at)
    db.session.add(this_repo)
    db.session.commit()

    add_languages(repo)
    #TODO: add_topics(repo)


def crawl_from_repo_to_users(repo):
    """Add repo, and add all users connected to that repo.

    Adds stargazers, watchers, and contributors."""

    # Note the start time to estimate time to complete process.
    start_time = datetime.datetime.now()

    # First, verify that repo is added to db.
    add_repo(repo)
    num_users = 1

    # Then crawl the graph out to connected users and add to db.
    num_users += add_stars(repo)
    num_users += add_watchers(repo)
    num_users += add_contributors(repo)

    end_time = datetime.datetime.now()
    time_delta = (end_time - start_time).total_seconds()
    time_delta = round(time_delta, 3)
    print("\r\x1b[K\n" + str(num_users) + " users loaded in " + str(time_delta) + " seconds.")


def update_repo(this_repo, new_repo):
    """Update repo if it hasn't been updated in more than 7 days."""

    delta = datetime.datetime.now().timestamp() - this_repo.updated_at.timestamp()
    if delta/60/60/24/7 < 1:
        print("Repo {} is up to date.".format(this_repo.name))
        return

    print("Updating old repo data for {}.".format(new_repo.name))

    this_repo.name = new_repo.name
    this_repo.description = new_repo.description

    db.session.add(this_repo)
    db.session.commit()


def is_repo_in_db(repo):
    """Check db for repo, and update xor return false."""

    this_repo = Repo.query.filter_by(repo_id=repo.id).first()
    if this_repo:
        print("Repo {} in db; updating.".format(repo.name))
        update_repo(this_repo, repo)
        return True
    return False


def add_user(user):
    """Query API, and update user details in db."""

    if is_user_in_db(user):
        return 0

    this_user = User(user_id=user.id,
                     name=user.name,
                     login=user.login,
                     created_at=user.created_at)
    db.session.add(this_user)
    db.session.commit()
    return 1


def update_user(this_user, new_user):
    """Update user if it hasn't been updated in more than 7 days."""

    delta = datetime.datetime.now().timestamp() - this_user.updated_at.timestamp()
    if delta/60/60/24/7 < 1:
        print("User {} is up to date.  ".format(this_user.login), end="\r\x1b[K")
        return

    print("Updating old user data for {}.".format(new_user.login), end="\r\x1b[K")

    this_user.name = new_user.name
    this_user.login = new_user.login

    db.session.add(this_user)
    db.session.commit()
    return


def is_user_in_db(user):
    """Check db for user, and update xor return false."""

    this_user = User.query.filter_by(user_id=user.id).first()
    if this_user:
        print("User {} in db; updating.".format(user.login), end="\r\x1b[K")
        update_user(this_user, user)
        return True
    return False


def add_stars(repo):
    """Add all stargazers of repo to db."""
    stars = repo.get_stargazers()
    num_stars = repo.stargazers_count
    num_users = 0

    msg = "Adding {} stargazers.".format(num_stars)
    bar = ShadyBar(msg, max=num_stars, suffix=progress_bar_suffix)

    for star in stars:
        num_users += add_user(star)

        this_star = Stargazer(repo_id=repo.id, user_id=star.id)
        db.session.add(this_star)
        db.session.commit()

        bar.next()
    bar.finish()
    return num_users


def add_watchers(repo):
    """Add all watchers of repo to db."""
    watchers = repo.get_watchers()
    num_watchers = repo.watchers_count
    num_users = 0

    msg = "Adding {} watchers.".format(num_watchers)
    bar = ShadyBar(msg, max=num_watchers, suffix=progress_bar_suffix)

    for watcher in watchers:
        num_users += add_user(watcher)

        this_watcher = Watcher(repo_id=repo.id, user_id=watcher.id)
        db.session.add(this_watcher)
        db.session.commit()

        bar.next()
    bar.finish()
    return num_users


def add_contributors(repo):
    """Add all contributors of repo to db."""
    contributors = repo.get_contributors()
    # num_contributors = repo.contributors_count
    num_users = 0

    msg = "Adding contributors."#.format(num_contributors)
    bar = Spinner(msg, suffix=progress_bar_suffix)

    for contributor in contributors:
        num_users += add_user(contributor)

        this_contributor = Contributor(repo_id=repo.id, user_id=contributor.id)
        db.session.add(this_contributor)
        db.session.commit()

        bar.next()
    bar.finish()
    return num_users


def add_lang(lang):
    """Add lang string to db."""
    this_lang = Language.query.filter_by(language_name=lang).first()

    if this_lang:
        return

    print("Adding lang {}.".format(lang))
    this_lang = Language(language_name=lang)
    db.session.add(this_lang)
    db.session.commit()


def add_repo_lang(repo, lang, num):
    """Add repo-lang association and number of bytes to db."""
    print("Adding repo-lang {}.".format(lang))
    this_lang = Language.query.filter_by(language_name=lang).first()
    this_repo_lang = RepoLanguage.query.filter_by(language_id=this_lang.language_id,
                                                  repo_id=repo.id).first()

    if this_repo_lang:
        this_repo_lang.language_bytes = num
        db.session.add(this_repo_lang)
        db.session.commit()

    this_repo_lang = RepoLanguage(repo_id=repo.id,
                                  language_id=this_lang.language_id,
                                  language_bytes=num)
    db.session.add(this_repo_lang)
    db.session.commit()


def add_languages(repo):
    """Add all languages of repo to db."""
    langs = repo.get_languages()

    for lang in langs.keys():
        add_lang(lang)
        add_repo_lang(repo, lang, langs[lang])


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(db_uri))

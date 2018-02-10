import os, datetime
import github
from progress.bar import ShadyBar
from progress.spinner import Spinner
import secrets
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)
# TODO: try Tenacity library

token = secrets.personal_access_token
client_id = secrets.client_id
client_secret = secrets.client_secret

g = github.Github(token, client_id=client_id, client_secret=client_secret)
progress_bar_suffix = "%(index)d/%(max)d, estimated %(eta)d seconds remaining."
spinner_suffix = "%(index)d added, avg %(avg)ds each, %(elapsed)d time elapsed."

# for repo in g.get_user().get_repos():
#     print(repo.name)
me = g.get_user()

def get_repo_object_from_input(repo_info)
    # If the argument is not a PyGithub repo object, get the PyGithub repo object:
    if type(repo_info) == github.Repository.Repository:
        return repo_info

    # If argument is an integer, assume it's the repo_id
    if type(repo_info) == int:
        repo_id = repo_info
    # If argument is model.Repo, get repo_id
    elif type(repo) == Repo:
        repo_id = repo_info.repo_id
    else:
        raise TypeError("expected id, string, or PyGithub user object, {} found".format(type(user)))
    
    # Return PyGithub repository object.
    return g.get_repo(repo_id)


def add_repo(repo_info):
    """Query API, and update repo details in db."""

    # If the argument is not a PyGithub repo object, get the PyGithub repo object:
    repo = get_repo_object_from_input(repo_info)

    if is_repo_in_db(repo):
        return 0

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
    return 1


def crawl_from_repo_to_users(repo_info):
    """Add repo, and add all users connected to that repo.

    Adds stargazers, watchers, and contributors."""

    # Note the start time to estimate time to complete process.
    start_time = datetime.datetime.now()

    # If the argument is not a PyGithub repo object, get the PyGithub repo object:
    repo = get_repo_object_from_input(repo_info)

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

    set_last_crawled_in_repo(repo.id, datetime.datetime.now())


def update_repo(this_repo, new_repo):
    """Update repo if it hasn't been updated in more than 7 days."""

    delta = datetime.datetime.now().timestamp() - this_repo.updated_at.timestamp()
    if delta/60/60/24/7 < 1:
        # print("Repo {} is up to date.".format(this_repo.name), end="\r\x1b[K")
        return

    # print("Updating old repo data for {}.".format(new_repo.name), end="\r\x1b[K")

    this_repo.name = new_repo.name
    this_repo.description = new_repo.description
    this_repo.updated_at = datetime.datetime.utcnow()

    db.session.add(this_repo)
    db.session.commit()


def is_repo_in_db(repo):
    """Check db for repo, and update xor return false."""

    this_repo = Repo.query.get(repo.id)
    if this_repo:
        # print("Repo {} in db; updating.".format(repo.name), end="\r\x1b[K")
        update_repo(this_repo, repo)
        return True
    return False


def set_last_crawled_in_repo(repo_id, last_crawled_time):
    """Set last_crawled to now() in repo."""
    this_repo = Repo.query.get(repo_id)
    this_repo.last_crawled = last_crawled_time

    db.session.add(this_repo)
    db.session.commit()


def get_user_object_from_input(user_info)
    if (type(user_info) == github.NamedUser.NamedUser or 
        type(user_info) == github.AuthenticatedUser.AuthenticatedUser):
        return user_info

    # If argument is an integer, assume it's the user_id:
    if type(user_info) == int:
        this_user = User.query.get(user_info)

        # If no user is in the database with this id, raise IOError.
        if not this_user:
            raise OSError("no user found with id {}".format(user_info))
        login = this_user.login

    # If argument is a string, assume it's the login:
    elif type(user_info) == str:
        login = user_info
    # If argument is a model.User object, get the login:
    elif type(user_info) == User:
        login = user_info.login
    else:
        raise TypeError("expected id, string, or PyGithub user object, {} found".format(type(user)))
    
    # Get the PyGithub user object.
    return g.get_user(login=login)


def add_user(user_info):
    """Query API, and update user details in db."""
    user = get_user_object_from_input(user_info)

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
        # print("User {} is up to date.  ".format(this_user.login), end="\r\x1b[K")
        return

    # print("Updating old user data for {}.".format(new_user.login), end="\r\x1b[K")

    this_user.name = new_user.name
    this_user.login = new_user.login
    this_user.updated_at = datetime.datetime.utcnow()

    db.session.add(this_user)
    db.session.commit()
    return


def is_user_in_db(user):
    """Check db for user, and update xor return false."""

    this_user = User.query.get(user.id)
    if this_user:
        # print("User {} in db; updating.".format(user.login), end="\r\x1b[K")
        update_user(this_user, user)
        return True
    return False


def set_last_crawled_in_user(user_id, last_crawled_time):
    """Set last_crawled to now() in user."""
    this_user = User.query.get(user_id)
    this_user.last_crawled = last_crawled_time

    db.session.add(this_user)
    db.session.commit()


def get_stars_from_repo(repo):
    return repo.get_stargazers()


def add_stars(repo):
    """Add all stargazers of repo to db."""
    stars = get_stars_from_repo(repo)
    num_stars = repo.stargazers_count
    num_users = 0

    msg = "Adding {} stargazers: ".format(num_stars)
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

    msg = "Adding {} watchers: ".format(num_watchers)
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

    msg = "Adding contributors: "#.format(num_contributors)
    bar = Spinner(msg, suffix=spinner_suffix)

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
    lang = lang.lower()
    this_lang = Language.query.filter_by(language_name=lang).first()

    if this_lang:
        return

    print("Adding lang {}.".format(lang))
    this_lang = Language(language_name=lang)
    db.session.add(this_lang)
    db.session.commit()


def add_repo_lang(repo_id, lang, num):
    """Add repo-lang association and number of bytes to db."""
    # print("Adding repo-lang {}.".format(lang))
    lang = lang.lower()
    this_lang = Language.query.filter_by(language_name=lang).first()
    this_repo_lang = RepoLanguage.query.filter_by(language_id=this_lang.language_id,
                                                  repo_id=repo_id).first()

    if this_repo_lang:
        this_repo_lang.language_bytes = num
        db.session.add(this_repo_lang)
        db.session.commit()
        return

    this_repo_lang = RepoLanguage(repo_id=repo_id,
                                  language_id=this_lang.language_id,
                                  language_bytes=num)
    db.session.add(this_repo_lang)
    db.session.commit()


def add_languages(repo):
    """Add all languages of repo to db."""
    langs = repo.get_languages()

    for lang in langs.keys():
        add_lang(lang)
        add_repo_lang(repo.id, lang, langs[lang])


def crawl_from_user_to_repos(user):
    """Add user, and add all repos connected to that user.

    Adds repos that are starred.

    This does not add a user's repos!"""

    # Note the start time to estimate time to complete process.
    start_time = datetime.datetime.now()

    # If the argument is not a PyGithub user object, get the PyGithub user object:
    user = get_user_object_from_input(user)

    # Verify that user is added to db.
    add_user(user)

    # Then crawl the graph out to starred repos and add to db.
    num_repos = add_starred_repos(user)

    end_time = datetime.datetime.now()
    time_delta = (end_time - start_time).total_seconds()
    time_delta = round(time_delta, 3)
    print("\r\x1b[K" + "\n{}repos loaded for {} in {} seconds.".format(num_repos, user.login, time_delta))

    set_last_crawled_in_user(user.id, datetime.datetime.now())


def get_starred_repos(user):
    """Get all repos starred by user from api."""
    return user.get_starred()


def add_starred_repos(user):
    """Add all repos starred by user to db."""
    stars = get_starred_repos(user)
    num_repos = 0

    msg = "Adding starred repositories for " + user.login + ": "
    bar = Spinner(msg, suffix=spinner_suffix)

    for star in stars:
        try:
            num_repos += add_repo(star)
        except BaseException as e:
            print("Error in add_starred_repos(): ", e)
            continue

        this_star = Stargazer(repo_id=star.id, user_id=user.id)
        db.session.add(this_star)
        db.session.commit()

        bar.next()
    bar.finish()
    return num_repos


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(db_uri))

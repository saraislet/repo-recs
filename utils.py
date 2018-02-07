import os, datetime
from github import Github
import secrets
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Topic, RepoTopic,
                   db, connect_to_db, db_uri)

token = secrets.personal_access_token
client_id = secrets.client_id
client_secret = secrets.client_secret

g = Github(token, client_id=client_id, client_secret=client_secret)

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

    add_stars(repo)
    add_watchers(repo)
    add_contributors(repo)


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
        return

    this_user = User(user_id=user.id,
                     name=user.name,
                     login=user.login,
                     created_at=user.created_at)
    db.session.add(this_user)
    db.session.commit()


def update_user(this_user, new_user):
    """Update user if it hasn't been updated in more than 7 days."""

    delta = datetime.datetime.now().timestamp() - this_user.updated_at.timestamp()
    if delta/60/60/24/7 < 1:
        print("User {} is up to date.".format(this_user.login))
        return

    print("Updating old user data for {}.".format(new_user.login))

    this_user.name = new_user.name
    this_user.login = new_user.login

    db.session.add(this_user)
    db.session.commit()


def is_user_in_db(user):
    """Check db for user, and update xor return false."""

    this_user = User.query.filter_by(user_id=user.id).first()
    if this_user:
        print("User {} in db; updating.".format(user.login))
        update_user(this_user, user)
        return True
    return False


def add_stars(repo):
    """Add all stargazers of repo to db."""
    stars = repo.get_stargazers()

    for star in stars:
        add_user(star)

        this_star = Stargazer(repo_id=repo.id, user_id=star.id)
        db.session.add(this_star)
        db.session.commit()


def add_watchers(repo):
    """Add all watchers of repo to db."""
    watchers = repo.get_watchers()

    for watcher in watchers:
        add_user(watcher)

        this_watcher = Watcher(repo_id=repo.id, user_id=watcher.id)
        db.session.add(this_watcher)
        db.session.commit()


def add_contributors(repo):
    """Add all contributors of repo to db."""
    contributors = repo.get_contributors()

    for contributor in contributors:
        add_user(contributor)

        this_contributor = Contributor(repo_id=repo.id, user_id=contributor.id)
        db.session.add(this_contributor)
        db.session.commit()


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(db_uri))

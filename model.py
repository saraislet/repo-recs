"""Models and database functions for git_data db."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
db_uri = "postgres:///git_data"


class Repo(db.Model):
    """Repository model."""

    __tablename__ = "repos"

    repo_id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True)

    owner = db.relationship("User",
                            backref=db.backref("repos", order_by=repo_id))

    stargazers = db.relationship("User",
                                 secondary='stargazers',
                                 order_by="User.user_id",
                                 backref=db.backref("stars", order_by=repo_id))

    watchers = db.relationship("User",
                               secondary='watchers',
                               order_by="User.user_id",
                               backref=db.backref("watches", order_by=repo_id))

    contributors = db.relationship("User",
                                   secondary='contributors',
                                   order_by="User.user_id",
                                   backref=db.backref("contributions", order_by=repo_id))

    topics = db.relationship("Topic",
                               secondary='repo_topics',
                               order_by="Topic.topic_name",
                               backref=db.backref("repos", order_by=repo_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Repo {} owner={} name={}>"
                .format(self.repo_id,
                        self.owner_id,
                        self.name))


class User(db.Model):
    """User model."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime(), nullable=True)
    updated_at = db.Column(db.DateTime(), nullable=True)
    
    followers = db.relationship("User",
                                secondary="followers",
                                order_by=user_id,
                                primaryjoin="User.user_id==followers.c.user_id",
                                secondaryjoin="User.user_id==followers.c.follower_id",
                                backref=db.backref("follows",
                                                   order_by=user_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<User {} login={} name={}>"
                .format(self.user_id,
                        self.login,
                        self.name))


class Follower(db.Model):
    """Watcher model."""

    __tablename__ = "followers"

    follow_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)
    follower_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Follower {} user_id={} follower_id={}>"
                .format(self.follow_id,
                        self.user_id,
                        self.follower_id))


class Stargazer(db.Model):
    """Stargazer model."""

    __tablename__ = "stargazers"

    stargazer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Stargazer {} repo_id={} user_id={}>"
                .format(self.stargazer_id,
                        self.repo_id,
                        self.user_id))


class Watcher(db.Model):
    """Watcher model."""

    __tablename__ = "watchers"

    watcher_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Watcher {} repo_id={} user_id={}>"
                .format(self.watcher_id,
                        self.repo_id,
                        self.user_id))


class Contributor(db.Model):
    """Contributor model."""

    __tablename__ = "contributors"

    contributor_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    user_id = db.Column(db.ForeignKey("users.user_id"), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Contributor {} repo_id={} user_id={}>"
                .format(self.contributor_id,
                        self.repo_id,
                        self.user_id))


class Topic(db.Model):
    """Topics model."""

    __tablename__ = "topics"

    topic_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<Topic {} name={}>"
                .format(self.topic_id,
                        self.topic_name))


class RepoTopic(db.Model):
    """Association table between Repository and Topic."""

    __tablename__ = "repo_topics"

    repo_topic_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    repo_id = db.Column(db.ForeignKey("repos.repo_id"), nullable=False)
    topic_id = db.Column(db.ForeignKey("topics.topic_name"), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return ("<RepoTopic {} repo_id={} topic_id={}>"
                .format(self.repo_topic_id,
                        self.repo_id,
                        self.topic_id))


def init_app():
    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB.")


def connect_to_db(app, uri=db_uri):
    """Connect the database to our Flask app."""

    # Configure to use our database.
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(db_uri))

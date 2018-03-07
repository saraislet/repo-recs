import datetime
import github
from github import GithubException
# from progress.bar import ShadyBar
import config, api_utils, db_utils
from model import (Repo, User, Follower, Account,
                   Stargazer, Dislike,
                   Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
# TODO: try Tenacity library

progress_bar_suffix = "%(index)d/%(max)d, estimated %(eta)d seconds remaining."

def get_repo_object_from_input(repo_info):
    # If the argument is not a PyGithub repo object, get the PyGithub repo object:
    if isinstance(repo_info, github.Repository.Repository):
        return repo_info

    # If argument is an integer, assume it's the repo_id
    if isinstance(repo_info, int):
        repo_id = repo_info
    # If argument is model.Repo, get repo_id
    elif isinstance(repo_info, Repo):
        repo_id = repo_info.repo_id
    else:
        raise TypeError("""expected id, Repo model object, or PyGithub user object, 
                           {} found.""".format(type(repo_info)))
    
    # Return PyGithub repository object.
    return api_utils.get_repo_from_api(repo_id)


def add_repo(repo_info, num_layers_to_crawl=0, force_refresh=False):
    """Query API, and update repo details in db."""

    # If the argument is not a PyGithub repo object, get the PyGithub repo object:
    try:
        repo = get_repo_object_from_input(repo_info)

        owner = repo.owner
        owner_id = owner.id
        # Must create User for owner before committing Repo to db.
        add_user(owner, num_layers_to_crawl)

        if db_utils.is_repo_in_db(repo.id):
            update_repo(repo, num_layers_to_crawl, force_refresh)
            return 0
        
        this_repo = Repo(repo_id=repo.id,
                         name=repo.name,
                         description=repo.description,
                         owner_id=owner.id,
                         created_at=repo.created_at,
                         updated_at=repo.updated_at,
                         last_updated=datetime.datetime.now(),
                         pushed_at=repo.pushed_at,
                         url=repo.url,
                         stargazers_count=repo.stargazers_count)
        db.session.add(this_repo)
        db.session.commit()

        db_utils.add_languages(repo)

        #TODO: A queue might be more robust than a recursive process.
        if num_layers_to_crawl:
            crawl_from_repo_to_users(repo, num_layers_to_crawl, force_refresh)

        return 1

    except TypeError as e:
        print("Error in add_repo({}): ".format(repo_info), e)
        return 0
    except GithubException as e:
        print("Error in add_repo({}): ".format(repo_info), e)
        return 0
    # except Exception as e:
        # print("Error in add_repo({}): ".format(repo_info), e)


def crawl_from_repo_to_users(repo_info, num_layers_to_crawl=0, force_refresh=False):
    """Add repo, and add all users connected to that repo.

    Adds stargazers, watchers, and contributors."""
    num_layers_to_crawl = max(0, num_layers_to_crawl - 1)

    # Note start time to estimate time to complete process.
    start_time = datetime.datetime.now()

    # If argument is not PyGithub repo object, get PyGithub repo object:
    repo = get_repo_object_from_input(repo_info)

    # First, verify that repo is added to db.
    add_repo(repo)
    num_users = 1

    # Check last crawled time and depth.
    # Verify repo is in db, and get repo object first.
    if (not force_refresh
        and db_utils.is_last_crawled_in_repo_good(repo.id,
                                                  1+num_layers_to_crawl)):
        return

    print("Crawling {} layers from repo {} ({})."
          .format(1+num_layers_to_crawl, repo.id, repo.name))

    # Then crawl the graph out to connected users and add to db.
    num_users += add_stars(repo, num_layers_to_crawl, force_refresh=True)
    # We may not need more details about a repo to make good suggestions, 
    # and most watchers are duplicates of stars.
    # num_users += add_watchers(repo, num_layers_to_crawl)
    # num_users += add_contributors(repo, num_layers_to_crawl)

    end_time = datetime.datetime.now()
    time_delta = (end_time - start_time).total_seconds()
    time_delta = round(time_delta, 3)
    print("{} users loaded in {} seconds."
          .format(num_users, time_delta))

    db_utils.set_last_crawled_in_repo(repo.id,
                                      datetime.datetime.now(),
                                      1+num_layers_to_crawl)


def update_repo(repo, num_layers_to_crawl=0, force_refresh=False):
    """Update repo if it hasn't been updated in more than 7 days."""
    this_repo = Repo.query.get(repo.id)

    if not this_repo:
        print(f"Repo not found! Adding repo {repo.name}")
        add_repo(repo)
        return

    delta = (datetime.datetime.now().timestamp()
             - this_repo.last_updated.timestamp())
    if (force_refresh
        or delta/60/60/24 > config.REFRESH_UPDATE_REPO_DAYS):

        this_repo.name = repo.name
        this_repo.description = repo.description
        this_repo.updated_at = repo.updated_at
        this_repo.pushed_at = repo.pushed_at
        this_repo.last_updated = datetime.datetime.now()
        this_repo.stargazers_count = repo.stargazers_count

        db_utils.add_languages(repo)

        db.session.add(this_repo)
        db.session.commit()

    #TODO: A queue might be more robust than a recursive process.
    if num_layers_to_crawl:
        crawl_from_repo_to_users(repo, num_layers_to_crawl, force_refresh)

    return


def get_user_object_from_input(user_info):
    if (isinstance(user_info, github.NamedUser.NamedUser) or 
        isinstance(user_info, github.AuthenticatedUser.AuthenticatedUser)):
        return user_info

    # If argument is an integer, assume it's the user_id:
    if isinstance(user_info, int):
        #TODO: This assumes that the user is in db. Check how this is handled.
        this_user = User.query.get(user_info)

        # If no user is in the database with this id, raise IOError.
        if not this_user:
            raise OSError("no user found with id {}".format(user_info))
        login = this_user.login

    # If argument is a string, assume it's the login:
    elif isinstance(user_info, str):
        login = user_info

    # If argument is a model.User object, get the login:
    elif isinstance(user_info, User):
        login = user_info.login

    else:
        raise TypeError("expected id, string, or PyGithub user object, {type(user_info)} found")
    
    # Get the PyGithub user object.
    return api_utils.get_user_from_api(login)


def add_user(user_info, num_layers_to_crawl=0):
    """Query API, and update user details in db."""
    try:    
        user = get_user_object_from_input(user_info)

        if db_utils.is_user_in_db(user.id):
            update_user(user, num_layers_to_crawl)
            return 0

        this_user = User(user_id=user.id,
                         name=user.name,
                         login=user.login,
                         created_at=user.created_at)
        db.session.add(this_user)
        db.session.commit()

        #TODO: A queue might be more robust than a recursive process.
        if num_layers_to_crawl:
            crawl_from_user_to_repos(user, num_layers_to_crawl)

        return 1
        
    except TypeError as e:
        print("Error in add_user({}): ".format(user_info), e)
        return 0
    except GithubException as e:
        print("Error in add_user({}): ".format(user_info), e)        
        return 0
    # except Exception as e:
    #     print("Error in add_user({}): ".format(user_info), e)        


def crawl_from_user_to_repos(user, num_layers_to_crawl=0, force_refresh=False):
    """Add user, and add all repos connected to that user.
    Adds repos that are starred.

    This does not add a user's repos!"""
    #TODO: check last crawled time and depth

    # Decrement the number of layers to crawl, until zero.
    num_layers_to_crawl = max(0, num_layers_to_crawl - 1)

    # Note the start time to estimate time to complete process.
    start_time = datetime.datetime.now()

    # If argument is not a PyGithub user object, get PyGithub user object.
    user = get_user_object_from_input(user)

    # Verify that user is added to db.
    add_user(user)

    # Check last crawled time and depth.
    # Verify repo is in db, and get repo object first.
    if (not force_refresh
        and db_utils.is_last_crawled_in_user_good(user.id,
                                                  1+num_layers_to_crawl)):
        return

    print("Crawling {} layers from user {} ({})."
          .format(1+num_layers_to_crawl, user.id, user.login))

    # Then crawl the graph out to starred repos and add to db.
    num_repos = add_starred_repos(user, num_layers_to_crawl, force_refresh)
    #TODO: crawl follows and followers
    # num_users = add_followers(user, num_layers_to_crawl)
    # num_users = add_follows(user, num_layers_to_crawl)

    end_time = datetime.datetime.now()
    time_delta = (end_time - start_time).total_seconds()
    time_delta = round(time_delta, 3)
    print("{} repos loaded for {} in {} seconds."
          .format(num_repos,
                  user.login,
                  time_delta))

    db_utils.set_last_crawled_in_user(user.id,
                                      datetime.datetime.now(),
                                      1+num_layers_to_crawl)


def update_user(user, num_layers_to_crawl=0, force_refresh=False):
    """Update user if it hasn't been updated in more than 7 days."""
    this_user = User.query.get(user.id)

    delta = (datetime.datetime.now().timestamp()
             - this_user.updated_at.timestamp())
    if (force_refresh
        or delta/60/60/24 > config.REFRESH_UPDATE_USER_DAYS):
        
        this_user.name = user.name
        this_user.login = user.login
        this_user.updated_at = datetime.datetime.utcnow()

        db.session.add(this_user)
        db.session.commit()

    #TODO: A queue might be more robust than a recursive process.
    if num_layers_to_crawl:
        crawl_from_user_to_repos(user, num_layers_to_crawl)

    return


def update_user_repos(user, num_layers_to_crawl=0, force_refresh=False):
    """Update user's repositories if they haven't been updated in more than 7 days."""

    # If argument is not a PyGithub user object, get PyGithub user object.
    user = get_user_object_from_input(user)

    this_user = User.query.get(user.id)

    delta = (datetime.datetime.now().timestamp()
             - this_user.updated_at.timestamp())
    if (force_refresh
        or delta/60/60/24 > config.REFRESH_UPDATE_USER_REPOS_DAYS):
        
        repos = api_utils.get_user_repos_from_api(user)

        for repo in repos:
            print(f"Updating repo: {repo.name}")
            update_repo(repo, force_refresh=force_refresh)

    db_utils.set_last_crawled_user_repos(user.id, datetime.datetime.now())

    #TODO: A queue might be more robust than a recursive process.
    if num_layers_to_crawl:
        crawl_from_user_to_repos(user, num_layers_to_crawl)

    return


def add_stars(repo, num_layers_to_crawl=0, force_refresh=False):
    """Add all stargazers of repo to db."""
    stars = api_utils.get_stargazers_from_api(repo)
    num_stars = repo.stargazers_count
    num_users = 0
    count = 0

    # msg = "Adding {} stargazers: ".format(num_stars)
    # bar = ShadyBar(msg, max=num_stars, suffix=progress_bar_suffix)

    for star in stars:
        # bar.next()
        count += 1
        if (num_users > config.MAX_CRAWL_COUNT_NEW
            or count > config.MAX_CRAWL_COUNT_TOTAL):
            break

        num_users += add_user(star, num_layers_to_crawl)

        # If star is in db, skip and continue.
        # TODO: Consider checking last_crawled of star.repo/star.user.
        this_star = Stargazer.query.filter_by(repo_id=repo.id,
                                              user_id=star.id).first()

        if this_star:
            #TODO: A queue might be more robust than a recursive process.
            if num_layers_to_crawl:
                crawl_from_user_to_repos(user, num_layers_to_crawl)
            continue

        this_star = Stargazer(repo_id=repo.id, user_id=star.id)
        db.session.add(this_star)
        db.session.commit()

    # bar.finish()
    return num_users


def add_watchers(repo, num_layers_to_crawl=0):
    """Add all watchers of repo to db."""
    watchers = repo.get_watchers()
    num_watchers = repo.watchers_count
    num_users = 0
    count = 0

    # msg = "Adding {} watchers: ".format(num_watchers)
    # bar = ShadyBar(msg, max=num_watchers, suffix=progress_bar_suffix)

    for watcher in watchers:
        # bar.next()
        count += 1
        if (num_users > config.MAX_CRAWL_COUNT_NEW
            or count > config.MAX_CRAWL_COUNT_TOTAL):
            break

        # If watcher is in db, skip and continue.
        # TODO: Consider checking last_crawled of watcher.repo/watcher.user.
        this_watcher = Watcher.query.filter_by(repo_id=repo.id,
                                               user_id=watcher.id).first()
        if this_watcher:
            #TODO: A queue might be more robust than a recursive process.
            if num_layers_to_crawl:
                crawl_from_user_to_repos(user, num_layers_to_crawl)
            continue

        num_users += add_user(watcher, num_layers_to_crawl)

        this_watcher = Watcher(repo_id=repo.id, user_id=watcher.id)
        db.session.add(this_watcher)
        db.session.commit()


    # bar.finish()
    return num_users


def add_contributors(repo, num_layers_to_crawl=0):
    """Add all contributors of repo to db."""
    contributors = repo.get_contributors()
    # num_contributors = repo.contributors_count
    num_users = 0
    count = 0

    # msg = "Adding contributors: "#.format(num_contributors)

    for contributor in contributors:
        count += 1
        if (num_users > config.MAX_CRAWL_COUNT_NEW
            or count > config.MAX_CRAWL_COUNT_TOTAL):
            break

        # If contributor is in db, skip and continue.
        # TODO: Consider checking last_crawled of contributor.repo/contributor.user.
        this_contributor = Contributor.query.filter_by(repo_id=repo.id,
                                                       user_id=contributor.id).first()
        if this_contributor:
            #TODO: A queue might be more robust than a recursive process.
            if num_layers_to_crawl:
                crawl_from_user_to_repos(user, num_layers_to_crawl)
            continue

        num_users += add_user(contributor, num_layers_to_crawl)

        this_contributor = Contributor(repo_id=repo.id,
                                       user_id=contributor.id)
        db.session.add(this_contributor)
        db.session.commit()

    return num_users


def add_starred_repos(user, num_layers_to_crawl=0, force_refresh=False):
    """Add all repos starred by user to db."""
    stars = api_utils.get_starred_repos_from_api(user)
    num_repos = 0
    count = 0

    # msg = "Adding starred repositories for " + user.login + ": "

    for star in stars:
        count += 1
        if (num_repos > config.MAX_CRAWL_COUNT_NEW
            or count > config.MAX_CRAWL_COUNT_TOTAL):
            break

        num_repos += add_repo(star, num_layers_to_crawl, force_refresh)

        # If star is in db, skip and continue.
        # TODO: Consider checking last_crawled of star.repo/star.user.
        this_star = Stargazer.query.filter_by(repo_id=star.id,
                                              user_id=user.id).first()

        if this_star:
            #TODO: A queue might be more robust than a recursive process.
            if num_layers_to_crawl:
                crawl_from_repo_to_users(this_star.repo_id,
                                         num_layers_to_crawl,
                                         force_refresh)
            continue

        this_star = Stargazer(repo_id=star.id, user_id=user.id)
        db.session.add(this_star)
        db.session.commit()

    return num_repos


if __name__ == "__main__":  # pragma: no cover
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    # So that we can use Flask-SQLAlchemy, we'll make a Flask app.
    from flask import Flask

    app = Flask(__name__)

    connect_to_db(app)
    print("Connected to DB {}.".format(config.DB_URI))

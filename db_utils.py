import datetime, json
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.sql import text
from model import (Repo, User, Follower, Account,
                   Stargazer, Dislike,
                   Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
import api_utils, config
import random


def get_ratings_from_db(debug=False):
    """Return list of ratings of repos by users."""
    query = """SELECT 
               CASE WHEN s.stargazer_id IS NULL THEN d.user_id ELSE s.user_id END AS user_id,
               CASE WHEN s.stargazer_id IS NULL THEN d.repo_id ELSE s.repo_id END AS repo_id,
               CASE WHEN s.stargazer_id IS NULL AND d.dislike_id IS NOT NULL THEN -1
               WHEN s.stargazer_id IS NOT NULL and d.dislike_id IS NOT NULL THEN 0
               WHEN s.stargazer_id IS NOT NULL and d.dislike_id IS NULL THEN 1
               ELSE -5 END AS rating
               FROM stargazers AS s FULL OUTER JOIN dislikes as d
               ON s.repo_id = d.repo_id AND s.user_id = d.user_id"""
    
    if debug:
        query += " ORDER BY rating, user_id, repo_id"
        query += " LIMIT 10"

    ratings = db.session.execute( text(query) ).fetchall()

    return ratings


def build_graph():
    """Return dictionary of graph nodes: source, target, names"""
    stars = Stargazer.query.options(joinedload(Stargazer.user),
                                    joinedload(Stargazer.repo)).all()
    
    nodes = []
    for star in stars:
        node1 = {"source": star.repo_id,
                 "target": star.user_id,
                 "source_name": star.repo.name,
                 "target_name": star.user.login,
                 "type": "repo-to-user"}
        node2 = {"source": star.user_id,
                 "target": star.repo_id,
                 "source_name": star.user.login,
                 "target_name": star.repo.name,
                 "type": "user-to-repo"}
        nodes.append(node1)
        nodes.append(node2)

    count = 4000
    skip = 20
    start = random.randrange(len(nodes) - count)
    return nodes[start:start+count:skip]

def build_graph1():
    """Return dictionary of graph nodes: source, target, names"""
    me = User.query.filter_by(login="Saraislet").first()
    cap = 20
    stars = set((me.stars_sec)[:cap])
    stars_to_add = set()

    for star in stars:
        new_stars = (star.repo.stargazers_sec)[:cap]
        stars_to_add.update(new_stars)
    stars.update(stars_to_add)

    nodes = []
    for star in stars:
        node1 = {"source": star.repo_id,
                 "target": star.user_id,
                 "source_name": star.repo.name,
                 "target_name": star.user.login,
                 "type": "repo-to-user"}
        node2 = {"source": star.user_id,
                 "target": star.repo_id,
                 "source_name": star.user.login,
                 "target_name": star.repo.name,
                 "type": "user-to-repo"}
        nodes.append(node1)
        # nodes.append(node2)

    # count = 4000
    # skip = 20
    # start = random.randrange(len(nodes) - count)
    # return nodes[start:start+count:skip]
    return nodes


def get_json_from_repos(repos):
    """Given list of Repo objects, return json."""
    data = []

    for repo in repos:
        language_data = []
        for lang in repo.repo_langs:
            lang_data = {"language_id": lang.language_id,
                         "language_name": lang.language.language_name,
                         "language_bytes": lang.language_bytes}
            language_data.append(lang_data)

        repo_data = {"repo_id": repo.repo_id,
                     "description": repo.description,
                     "name": repo.name,
                     "owner_login": repo.owner.login,
                     "stargazers_count": repo.stargazers_count,
                     "url": repo.url,
                     "langs": language_data}
        data.append(repo_data)
    return json.dumps(data)


def filter_stars_from_repo_ids(repo_ids, user_id):
    """Remove repo_ids starred by the user and return remaining."""
    stars = Stargazer.query.filter_by(user_id=user_id)
    stars = stars.with_entities(Stargazer.repo_id).all()
    star_ids = [star.repo_id for star in stars]

    return [repo_id for repo_id in repo_ids if repo_id not in star_ids]


def is_repo_in_db(repo_id):
    """Check db for repo, return true or false."""

    this_repo = Repo.query.get(repo_id)
    if this_repo:
        return True
    return False


def is_user_in_db(user_id):
    """Check db for user, and update xor return false."""

    this_user = User.query.get(user_id)
    if this_user:
        return True
    return False


def set_last_crawled_in_user(user_id, last_crawled_time, last_crawled_depth):
    """Set last_crawled to now() in user."""
    this_user = User.query.get(user_id)
    this_user.last_crawled = last_crawled_time
    this_user.last_crawled_depth = last_crawled_depth

    db.session.add(this_user)
    db.session.commit()


def set_last_crawled_user_repos(user_id, last_crawled_time):
    """Set last_crawled_user_repos to now() in user."""
    this_user = User.query.get(user_id)
    this_user.last_crawled_user_repos = last_crawled_time

    db.session.add(this_user)
    db.session.commit()


def is_last_crawled_in_user_good(user_id, crawl_depth, crawled_since=None):
    """Return boolean identifying if user must be crawled further now."""
    # If a crawl soon after has a lower depth, we don't need to crawl,
    # but a deeper crawl will need to crawl from here further.

    this_user = User.query.get(user_id)
    if (not this_user.last_crawled_depth
        or not this_user.last_crawled
        or this_user.last_crawled_depth < crawl_depth):
        return False

    if (crawled_since
        and crawled_since.timestamp() > this_user.last_crawled.timestamp()):
        return False

    delta = datetime.datetime.now().timestamp() - this_user.last_crawled.timestamp()
    if delta/60/60/24 > config.REFRESH_UPDATE_USER_DAYS:
        return False

    return True


def is_last_crawled_user_repos_good(user_id, crawled_since=None):
    """Return boolean identifying if user must be crawled further now."""
    # If a crawl soon after has a lower depth, we don't need to crawl,
    # but a deeper crawl will need to crawl from here further.

    this_user = User.query.get(user_id)
    if not this_user.last_crawled_user_repos:
        return False

    if (crawled_since
        and crawled_since > this_user.last_crawled_user_repos):
        return False

    delta = datetime.datetime.now().timestamp() - this_user.last_crawled_user_repos.timestamp()
    if delta/60/60/24 > config.REFRESH_UPDATE_USER_REPOS_DAYS:
        return False

    return True


def set_last_crawled_in_repo(repo_id, last_crawled_time, last_crawled_depth):
    """Set last_crawled to now() in repo."""
    # If a crawl soon after has a lower depth, we don't need to crawl,
    # but a deeper crawl will need to crawl from here further.

    this_repo = Repo.query.get(repo_id)
    this_repo.last_crawled = last_crawled_time
    this_repo.last_crawled_depth = last_crawled_depth

    db.session.add(this_repo)
    db.session.commit()


def is_last_crawled_in_repo_good(repo_id, crawl_depth, crawled_since=None):
    """Return boolean identifying if repo must be crawled further now."""
    # If a crawl soon after has a lower depth, we don't need to crawl,
    # but a deeper crawl will need to crawl from here further.

    this_repo = Repo.query.get(repo_id)
    if (not this_repo.last_crawled_depth or 
        not this_repo.last_crawled or
        this_repo.last_crawled_depth < crawl_depth):
        return False

    if (crawled_since
        and crawled_since.timestamp() > this_repo.last_crawled.timestamp()):
        return False


    delta = datetime.datetime.now().timestamp() - this_repo.last_crawled.timestamp()
    if delta/60/60/24 > config.REFRESH_UPDATE_REPO_DAYS:
        return False

    return True


def account_login(user, access_token):
    """Add account to db."""
    this_account = Account.query.filter_by(user_id=user.id).first()
    if this_account:
        this_account.last_login = datetime.datetime.now()
        this_account.access_token = access_token
        db.session.add(this_account)
        db.session.commit()
        return

    this_account = Account(user_id=user.id,
                           access_token=access_token,
                           last_login=datetime.datetime.now())
    db.session.add(this_account)
    db.session.commit()
    return


def add_stargazer(repo_id, user_id):
    """Add stargazer to database."""
    try:
        this_star = Stargazer(repo_id=repo_id, user_id=user_id)
        db.session.add(this_star)
        db.session.commit()
        print(f"Added star to database: repo {repo_id}, user {user_id}.")
    except IntegrityError as e:
        print(f"Star exists for repo {repo_id}, user {user_id}.")
        db.session.rollback()


def remove_stargazer(repo_id, user_id):
    """Remove stargazer from database."""
    this_star = Stargazer.query.filter_by(repo_id=repo_id,
                                          user_id=user_id).first()
    
    if not this_star:
        print(f"No star in database to remove: repo {repo_id}, user {user_id}.")
        return

    db.session.delete(this_star)
    db.session.commit()
    print(f"Removed star from database: repo {repo_id}, user {user_id}.")


def add_dislike(repo_id, user_id):
    """Add dislike to database."""
    try:
        this_dislike = Dislike(repo_id=repo_id, user_id=user_id)
        db.session.add(this_dislike)
        db.session.commit()
        print(f"Added dislike to database: repo {repo_id}, user {user_id}.")
    except IntegrityError as e:
        print(f"Dislike exists for repo {repo_id}, user {user_id}.")
        db.session.rollback()


def remove_dislike(repo_id, user_id):
    """Remove dislike from database."""
    this_dislike = Dislike.query.filter_by(repo_id=repo_id,
                                          user_id=user_id).first()
    
    if not this_dislike:
        print(f"No dislike in database to remove: repo {repo_id}, user {user_id}.")
        return

    db.session.delete(this_dislike)
    db.session.commit()
    print(f"Removed dislike from database: repo {repo_id}, user {user_id}.")


def add_lang(lang):
    """Add lang string to db."""
    this_lang = Language.query.filter(Language.language_name.ilike(lang)).first()

    if this_lang:
        return

    this_lang = Language(language_name=lang)
    db.session.add(this_lang)
    db.session.commit()


def add_repo_lang(repo_id, lang, num):
    """Add repo-lang association and number of bytes to db."""
    this_lang = Language.query.filter(Language.language_name.ilike(lang)).first()
    this_repo_lang = RepoLanguage.query.filter_by(language_id=this_lang.language_id,
                                                  repo_id=repo_id).first()

    if this_repo_lang:
        this_repo_lang.language_bytes = num
        db.session.add(this_repo_lang)
        db.session.commit()
        print(f"RepoLanguage updated: {this_repo_lang}")
        return

    this_repo_lang = RepoLanguage(repo_id=repo_id,
                                  language_id=this_lang.language_id,
                                  language_bytes=num)
    db.session.add(this_repo_lang)
    db.session.commit()


def add_languages(repo):
    """Add all languages of repo to db."""
    langs = api_utils.get_languages_from_api(repo)

    for lang in langs.keys():
        add_lang(lang)
        add_repo_lang(repo.id, lang, langs[lang])

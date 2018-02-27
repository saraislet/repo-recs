import datetime, json
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)
import api_utils, config


def get_ratings_from_db():
    """Return list of ratings of repos by users."""
    ratings = Stargazer.query.all()
    return [ [rating.user_id, rating.repo_id, 1] for rating in ratings ]


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
        and crawled_since.timestamp() > this_user.last_crawled.timestamp()):
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
    this_star = Stargazer(repo_id=repo_id, user_id=user_id)
    db.session.add(this_star)
    db.session.commit()
    print("Added star to database: repo {}, user {}."
          .format(repo_id, user_id))


def remove_stargazer(repo_id, user_id):
    """Remove stargazer from database."""
    this_star = Stargazer.query.filter_by(repo_id=repo_id,
                                          user_id=user_id).first()
    db.session.delete(this_star)
    db.session.commit()
    print("Removed star from database: repo {}, user {}."
          .format(repo_id, user_id))


def add_lang(lang):
    """Add lang string to db."""
    # lang = lang.lower()
    this_lang = Language.query.filter(Language.language_name.ilike(lang)).first()

    if this_lang:
        return

    # print("Adding lang {}.".format(lang))
    this_lang = Language(language_name=lang)
    db.session.add(this_lang)
    db.session.commit()


def add_repo_lang(repo_id, lang, num):
    """Add repo-lang association and number of bytes to db."""
    # print("Adding repo-lang {}.".format(lang))
    lang = lang.lower()
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

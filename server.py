import datetime, json, os, requests, urllib
from flask import (Flask, flash, redirect, render_template,
                   request, session)
from jinja2 import StrictUndefined
import config, rec, utils, api_utils, db_utils
from model import (Repo, User, Follower, Account,
                   Stargazer, Dislike,
                   Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db)

if not os.environ.get("CLIENT_ID"):
    import secrets2
    print(os.environ.get("CLIENT_ID"))

app = Flask(__name__)
app.secret_key = "temp"
# Don't let undefined variables fail silently.
app.jinja_env.undefined = StrictUndefined
# With old Flask versions, this may be necessary to auto-reload changes.
#app.jinja_env.auto_reload = True

@app.route("/")
def main():
    return render_template("home.html")


@app.route("/about")
def about():
    flash("Oops! Not available yet.")
    return redirect("/")


@app.route("/me")
def get_my_profile():
    if "user_id" not in session:
        return redirect("/")

    return get_user_profile(session["user_id"])


@app.route("/user", methods=["GET"])
def get_user():
    user_id = request.args.get("user_id")
    login = request.args.get("login")

    if user_id:
      user_id = int(user_id)

    return get_user_profile(user_id=user_id, login=login)


def get_user_profile(user_id="", login=""):
    user = None

    if user_id:
        user = User.query.get(user_id)
    elif login:
        user = User.query.filter_by(login=login).first()
        if not user:
            user = User.query.filter(User.login.ilike(login)).first()

    if not user:
        flash("Unable to find user (id:{}, login:{}).".format(user_id, login))
        return redirect("/")

    return render_template("user_info.html",
                           user=user,
                           repos=user.repos)


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        flash("Logged out.")

    return redirect("/")


@app.route("/login")
def login():
    if "user_id" in session:
        return redirect("/")

    session["state"] = "foo"
    #TODO: set this to random string when OAuth is working.
    payload = {"client_id": os.environ.get("CLIENT_ID"),
               "state": session["state"],
               "redirect_uri": config.AUTH_CALLBACK_URL,
               "scope": config.OAUTH_SCOPE}

    # print("Preparing OAuth get code request.")
    p = requests.Request("GET", 
                         config.GITHUB_AUTH_REQUEST_CODE_URL,
                         params=payload).prepare()
    return redirect(p.url)


@app.route("/auth", methods=["GET"])
def auth():
    if "user_id" in session:
        return redirect("/")

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or state != session.get("state"):
        flash("""Oops. We couldn't authorize your Github account; 
                 please try again.""")
        return redirect("/")

    print("Preparing OAuth post request for access token.")
    payload = {"client_id": os.environ.get("CLIENT_ID"),
               "client_secret": os.environ.get("CLIENT_SECRET"),
               "code": code,
               "state": session["state"],
               "redirect_uri": config.AUTH_CALLBACK_URL,
               "scope": config.OAUTH_SCOPE}

    r = requests.post(config.GITHUB_AUTH_REQUEST_TOKEN_URL, params=payload)
    print(r.text)
    access_token =  urllib.parse.parse_qs(r.text).get("access_token")
    if not access_token:
        flash("""Oops. We couldn't authorize your Github account; 
                 please try again.""")
        return redirect("/")
    access_token = access_token[0]

    g = api_utils.get_auth_api(access_token)
    user = g.get_user()
    utils.add_user(user)
    db_utils.account_login(user, access_token)
    session["user_id"] = user.id
    session["access_token"] = access_token

    flash("Successfully authenticated {} with Github!".format(user.login))
    return redirect("/")


@app.route("/recs", methods=["GET"])
def get_repo_recs_react():
    if "user_id" not in session:
        return redirect("/")

    limit = int(request.args.get("count", config.DEFAULT_COUNT))
    # offset = limit * (-1 + int(request.args.get("page", 1)))
    page = int(request.args.get("page", 1))
    login = request.args.get("login")
    user_id = request.args.get("user_id")
    if user_id:
        user_id = int(user_id)

        # If user_id parameter is included but not in database, redirect.
        if not utils.is_user_in_db(user_id):
            flash("No user found with id {}.".format(user_id))
            return redirect("/") 
        print("Using user_id {} for recs.".format(user_id))
        

    # Login parameter takes precedence.
    if login:
        if User.query.filter_by(login=login).count() == 0:
            flash("No user found with login {}.".format(login))
            return redirect("/")
        user_id = User.query.filter_by(login=login).first().user_id
        print("Using login {} for user_id {} for recs."
              .format(login, user_id))
    elif not user_id:
        user_id = session["user_id"]
        print("Using logged in user {} for recs.".format(user_id))

    return render_template("repo_recs_json.html",
                           user_id=user_id,
                           count=limit,
                           page=page)


@app.route("/get_repo_recs", methods=["GET"])
def get_repo_recs_json():
    """Return JSON of repo recommendations for a user_id or login."""
    if "user_id" not in session:
        return redirect("/")

    limit = int(request.args.get("count", config.DEFAULT_COUNT))
    offset = limit * (-1 + int(request.args.get("page", 1)))
    login = request.args.get("login")
    user_id = request.args.get("user_id")
    if user_id:
        user_id = int(user_id)

        # If user_id parameter is included but not in database, redirect.
        if not utils.is_user_in_db(user_id):
            flash("No user found with id {}.".format(user_id))
            return redirect("/") 
        print("Using user_id {} for recs.".format(user_id))
        
    # Login parameter takes precedence.
    if login:
        if User.query.filter_by(login=login).count() == 0:
            flash("No user found with login {}.".format(login))
            return redirect("/")
        user_id = User.query.filter_by(login=login).first().user_id
        print("Using login {} for user_id {} for recs."
              .format(login, user_id))
    elif not user_id:
        user_id = session["user_id"]
        print("Using logged in user {} for recs.".format(user_id))

    recs = rec.get_repo_suggestions(user_id)[offset:2*limit]
    filtered_recs = db_utils.filter_stars_from_repo_ids(recs, user_id)

    repos_query = Repo.query.filter(Repo.repo_id.in_(filtered_recs),
                                    Repo.owner_id != user_id)
    repos = repos_query.all()

    return db_utils.get_json_from_repos(repos[0:limit])


@app.route("/add_star", methods=["POST"])
def add_star():
    if "user_id" not in session or "access_token" not in session:
        flash("Please log in with your GitHub account.")
        return redirect("/")

    data = request.get_json()
    repo_id = data["repo_id"]
    access_token = session["access_token"]
    g = api_utils.get_auth_api(access_token)
    repo = g.get_repo(repo_id)
    user = g.get_user()
    user.add_to_starred(repo)

    if not user.has_in_starred(repo):
        flash("Unable to star this repo ({}). Please try again later."
              .format(repo.name))
        print("User {} was unable to star repo {} ({})"
              .format(user.login,
                      repo.name,
                      repo.id))
        return json.dumps({"Status": 404,
                           "action": "add_star",
                           "repo_id": repo.id})

    db_utils.add_stargazer(repo_id, session["user_id"])
    print("User {} sucessfully added a star for repo {} ({})"
          .format(user.login,
                  repo.name,
                  repo.id))
    return json.dumps({"Status": 204,
                       "action": "add_star",
                       "repo_id": repo.id})


@app.route("/remove_star", methods=["POST"])
def remove_star():
    if "user_id" not in session or "access_token" not in session:
        flash("Please log in with your GitHub account.")
        return redirect("/")

    data = request.get_json()
    repo_id = data["repo_id"]
    access_token = session["access_token"]
    g = api_utils.get_auth_api(access_token)
    repo = g.get_repo(repo_id)
    user = g.get_user()
    user.remove_from_starred(repo)

    if user.has_in_starred(repo):
        flash("Unable to unstar this repo ({}). Please try again later."
              .format(repo.name))
        print("User {} was unable to unstar repo {} ({})"
              .format(user.login,
                      repo.name,
                      repo.id))
        return json.dumps({"Status": 404,
                           "action": "remove_star",
                           "repo_id": repo.id})

    db_utils.remove_stargazer(repo_id, session["user_id"])
    print("User {} sucessfully unstarred repo {} ({})"
          .format(user.login,
                  repo.name,
                  repo.id))
    return json.dumps({"Status": 204,
                       "action": "remove_star",
                       "repo_id": repo.id})

@app.route("/check_star", methods=["POST"])
def check_star():
    if "user_id" not in session or "access_token" not in session:
        flash("Please log in with your GitHub account.")
        return redirect("/")

    repo_id = int(request.args.get("repo_id"))

    g = api_utils.get_auth_api(session["access_token"])
    user = g.get_user()
    print(user, user.login, user.name)
    repo = utils.get_repo_object_from_input(repo_id)
    print(repo, repo_id, repo.name)
    print(user.has_in_starred(repo))
    if user.has_in_starred(repo):
        return json.dumps({"Status": 204,
                           "action": "check_star",
                           "repo_id": repo.id})

    return json.dumps({"Status": 404,
                       "action": "check_star",
                       "repo_id": repo.id})


@app.route("/add_dislike", methods=["POST"])
def add_dislike():
    if "user_id" not in session or "access_token" not in session:
        flash("Please log in with your GitHub account.")
        return redirect("/")

    data = request.get_json()
    repo_id = data.get("repo_id")
    user_id = session["user_id"]
    
    db_utils.add_dislike(repo_id, user_id)

    print(f"User {user_id} sucessfully added a star for repo {repo_id}.")
    return json.dumps({"Status": 204,
                       "action": "add_dislike",
                       "repo_id": repo_id})


@app.route("/remove_dislike", methods=["POST"])
def remove_dislike():
    if "user_id" not in session or "access_token" not in session:
        flash("Please log in with your GitHub account.")
        return redirect("/")

    data = request.get_json()
    repo_id = data["repo_id"]
    user_id = session["user_id"]

    db_utils.remove_dislike(repo_id, user_id)

    print(f"User {user_id} sucessfully removed a star for repo {repo_id}.")
    return json.dumps({"Status": 204,
                       "action": "remove_dislike",
                       "repo_id": repo_id})


@app.route("/update_user", methods=["POST"])
def update_user():
    user_id = session.get("user_id")

    if user_id:
      user_id = int(user_id)

      crawled_since = (datetime.datetime.now()
                       - datetime.timedelta(days = config.REFRESH_UPDATE_USER_REPOS_DAYS))

      if not db_utils.is_last_crawled_in_user_good(user_id, 1, crawled_since):
          print(f"Updating user {user_id}.")
          utils.update_user_repos(user_id, force_refresh=True)
          utils.crawl_from_user_to_repos(user_id, force_refresh=True)
          print(f"User {user_id} updated.")

          return json.dumps({"Status": 200,
                             "action": "update_user",
                             "message": "User updated."})

      print(f"User {user_id} is up-to-date.")
      return json.dumps({"Status": 200,
                         "action": "update_user",
                         "message": "User up-to-date."})

    return json.dumps({"Status": 400,
                       "action": "update_user",
                       "message": "No user_id."})


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    connect_to_db(app)

    app.run(port=5000)

import json, requests, urllib
from flask import Flask, flash, redirect, render_template, request, session
from jinja2 import StrictUndefined
import github
import secrets, utils
from model import (Repo, User, Follower,
                   Stargazer, Watcher, Contributor,
                   Language, RepoLanguage,
                   db, connect_to_db, db_uri)

github_auth_request_code_url = "https://github.com/login/oauth/authorize"
github_auth_request_token_url = "https://github.com/login/oauth/access_token"
auth_callback_url = "http://127.0.0.1:5000/auth"
oauth_scope = "user user:follow read:user"
endpoint = "https://api.github.com"
authenticated_user_path = "/user"

app = Flask(__name__)
app.secret_key = "temp"
# Don't let undefined variables fail silently.
app.jinja_env.undefined = StrictUndefined

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

    user = User.query.get(session["user_id"])
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
    payload = {"client_id": secrets.client_id,
               "state": session["state"],
               "redirect_uri": auth_callback_url,
               "scope": oauth_scope}

    print("Preparing OAuth get code request.")
    p = requests.Request("GET", 
                         github_auth_request_code_url,
                         params=payload).prepare()
    return redirect(p.url)

@app.route("/auth")
def auth():
    if "user_id" in session:
        return redirect("/")

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or state != session.get("state"):
        flash("Oops. We couldn't authorize your Github account; please try again.")
        return redirect("/")

    print("Preparing OAuth post request for access token.")
    payload = {"client_id": secrets.client_id,
               "client_secret": secrets.client_secret,
               "code": code,
               "state": session["state"],
               "redirect_uri": auth_callback_url,
               "scope": oauth_scope}

    r = requests.post(github_auth_request_token_url, params=payload)
    print(r.text)
    access_token =  urllib.parse.parse_qs(r.text).get("access_token")
    if not access_token:
        flash("Oops. We couldn't authorize your Github account; please try again.")
        return redirect("/")
    access_token = access_token[0]

    g = github.Github(access_token,
                      client_id=secrets.client_id,
                      client_secret=secrets.client_secret)
    user = g.get_user()
    utils.add_user(user)
    session["user_id"] = user.id

    # print("Getting user data from Github API.")
    # payload = {"access_token": access_token}
    # path = endpoint + authenticated_user_path

    # r = requests.get(path, params=payload,
    #                  headers={'Authorization': 'token ' + access_token})

    # print("Adding authenticated user ({}) to db.".format(user_data.get("id")))
    # user_data = json.loads(r.text)
    # session["user_id"] = user_data.get("id")
    # utils.add_user(user_data.get("login"))

    flash("Successfully authenticated {} with Github!".format(user.login))
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    connect_to_db(app)


    # app.run(port=5000, host='0.0.0.0')
    app.run(port=5000)

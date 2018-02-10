import json, requests
from flask import Flask, flash, redirect, render_template, request, session
from jinja2 import StrictUndefined
import github
import secrets, utils
from model import connect_to_db

github_auth_request_code_url = "https://github.com/login/oauth/authorize"
github_auth_request_token_url = "https://github.com/login/oauth/access_token"
auth_callback_url = "http://127.0.0.1:5000/auth"
oauth_scope = "user:follow read:user"
endpoint = "https://api.github.com"
authenticated_user_path = "/user"

app = Flask(__name__)
app.secret_key = "temp"
# Don't let undefined variables fail silently.
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def main():
    return render_template("home.html")


@app.route("/me")
def get_my_profile():
    if "user_id" not in session:
        return redirect("/")
    return render_template("home.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]

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
    access_token = request.args.get("access_token")

    if not code or state != session.get("state"):
        print("Oops. We couldn't authorize your Github account; please try again.")
        flash("Oops. We couldn't authorize your Github account; please try again.")
        return redirect("/")

    if access_token:
        print("Received access token: ", access_token)
        session["access_token"] = access_token
        print("Successfully authenticated with Github!!")
        flash("Successfully authenticated with Github!!")
        return redirect("/")

    print("Preparing OAuth post request for access token.")
    payload = {"client_id": secrets.client_id,
               "client_secret": secrets.client_secret,
               "code": code,
               "state": session["state"],
               "redirect_uri": auth_callback_url,
               "scope": oauth_scope}

    r = requests.post(github_auth_request_token_url, params=payload)
    print(r.content)

    g = github.Github(access_token,
                      client_id=secrets.client_id,
                      client_secret=secrets.client_secret)
    # user = g.get_user()
    # utils.add_user(user)

    payload = {"access_token": access_token}
    path = endpoint + authenticated_user_path
    r = requests.get(path, params=payload)
    print(type(r.text), type(r.content))
    user_data = json.loads(r.text)
    utils.add_user(user_data.get("id"))

    session["user_id"] = user_data.get("id")

    print("Successfully authenticated {} with Github!".format(user_data.get("login")))
    flash("Successfully authenticated {} with Github!".format(user_data.get("login")))

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

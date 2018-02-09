from flask import Flask, flash, redirect, render_template, session

app = Flask(__name__)
app.secret_key = "temp"
# Don't let undefined variables fail silently.
app.jinja_env.undefined = StrictUndefined

@app.route("/")
def main():
    return render_template("base.html")


@app.route("/me")
def get_my_profile():
    if "user_id" not in session:
        return redirect("/")
    return render_template("base.html")


@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]

    return redirect("/")


@app.route("/login")
def logout():
    if "user_id" in session:
        return redirect("/")

    return render_template("login.html")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    # app.debug = True
    
    # make sure templates, etc. are not cached in debug mode
    # app.jinja_env.auto_reload = app.debug

    # Use the DebugToolbar
    # DebugToolbarExtension(app)

    # connect_to_db(app)


    app.run(port=5000, host='0.0.0.0')

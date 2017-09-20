"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, jsonify, render_template,
                redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Rating, Movie


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route("/users")
def user_list():
    """Show list of users."""

    users= User.query.all()
    return render_template("user_list.html", users=users)


@app.route("/register", methods=["GET"])
def register_form():
    """Displays registration form"""

    return render_template("register_form.html")


@app.route("/register", methods=["POST"])
def register_process():
    """Processes registration, adding user to DB if do not exist already"""


    email = request.form.get("email")
    password = request.form.get("password")

    user_check = User.query.filter_by(email=email).all()


    if user_check == []:
        new_user = User(email=email,password = password)
        db.session.add(new_user)

    db.session.commit()

    return redirect("/")

@app.route("/login")
def login_form():
    """Displays login form"""

    return render_template("login_form.html")


@app.route("/login", methods=["POST"])
def login_handler():
    """Handles login form inputs, if valid login credentials
    redirect to homepage and flash message
    """
    #if password and email are in database redirect to homepage and
    #add user id to flask session and flash message

    email = request.form.get("email")
    password = request.form.get("password")



    if User.query.filter_by(email=email, password=password).all():
        currentuser = User.query.filter_by(email=email).one()
        session["User ID"] = currentuser.user_id
        flash("You are currently logged in")
    return redirect("/")


@app.route("/logout")
def logout_handler():
    """logs users out"""
    session.pop("User ID", None)
    print session
    flash("You are currently logged out")
    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)



    app.run(port=5000, host='0.0.0.0')

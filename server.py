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
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        ## add flash and redirect to sign in page if exists
    else:
        flash('Looks like you already have an account. Sign in!')
        return redirect("/login")

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

    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if user:
        if user.password == password:
            session["User ID"] = user.user_id
            flash("You are currently logged in")
        else:
            flash("Incorrect password")
            return redirect("/login")
    else:
        flash("email doesn't exist")
        return redirect("/register")
    return redirect("/userdetails/%s" % user.user_id)


@app.route("/logout")
def logout_handler():
    """logs users out"""
    session.pop("User ID", None)
    print session
    flash("You are currently logged out")
    return redirect("/")


@app.route("/userdetails/<user_id>")
def user_info(user_id):
    """Display user age, zipcode, rated movies & scores"""


    user = User.query.filter_by(user_id=user_id).one()

    user_zipcode = user.zipcode
    user_age = user.age

    movie_ratings = {}
    for rating in user.ratings:
        title = rating.movie.title
        score = rating.score
        movie_ratings[title] = score
    print movie_ratings

    return render_template("user_details.html", user_zipcode=user_zipcode, user_age=user_age, movie_ratings=movie_ratings)


@app.route("/movielist")
def movie_list():
    """Displays long list of all the movies"""
    movies = Movie.query.order_by('title').all()


    return render_template("movie_list.html", movies=movies)


@app.route("/moviedetails/<movie_id>", methods=['GET'])
def movie_details(movie_id):
    """Display movie details and allow logged in users to rate"""
    movie = Movie.query.filter_by(movie_id=movie_id).one()

    if session == {}:
        loggedin = "False"
    else:
        loggedin = "True"



    return render_template("movie_details.html", movie=movie, loggedin=loggedin)

@app.route("/moviedetails/<movie_id>", methods=["POST"])
def rating_handler(movie_id):
    """Handle submissions from rating form & make updates, then redirect to movie details page"""

    rating = request.form.get("rating")

    user = User.query.filter_by(user_id=session["User ID"]).one()
    print "hello"
    for rating in user.ratings:
        print rating, "RATING"
        print rating.movie_id, 'Rating . movie id'
        print movie_id, "MOVIE ID"

        if rating.movie_id == movie_id:
            curr_rating = rating
            print rating, "RATING"
        else:
            print "NOT Yet Rated"


    #check if user_id in rating already


    #if from the session we see they are not logged in
    #hold form back and flash message to login or set form to disabled
    #if logged in then update score if user rated previously or create new rating

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

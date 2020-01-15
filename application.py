import os

from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from helpers import login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
#@login_required
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # Forget any user_id
    session.clear()
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    #check if user exists in the db
    error = None
    if request.method=='POST':
        if db.execute("SELECT * FROM users WHERE email=:email", {"email":email}).rowcount==1:
            error = "Email already in use, please try to login"
            return render_template("register.html", name=name,email=email,password=password, error=error)
        else:
            #commit user in the db
            db.execute("insert into users (first_name,email,password) values(:name, :email,:password)",
                        {"name": name, "email": email, "password": password})
            db.commit()
            return redirect("/login")
#            return render_template("register_confirmation.html", name=name, email=email, password=password)
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    email = request.form.get("email")
    password = request.form.get("password")
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            error = "must provide email"
            return render_template("/login.html", email=email, error=error)

        # Ensure password was submitted
        elif not request.form.get("password"):
            error = "must provide password"
            return render_template("login.html", error=error, password=password)

        rows = db.execute("SELECT * FROM users WHERE email = :email",
                            {"email": email})
        
        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result == None or not request.form.get("password"):
            return render_template("login.html", message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    return render_template("login.html")


@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")
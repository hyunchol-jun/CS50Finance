from flask import Flask, render_template, redirect, session, request
from flask_session import Session
from tempfile import mkdtemp
from helpers import login_required, apology

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear() # Forget any user_id

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:    # Ensure username was submitted
            return apology("must provide username", 403)
        elif not password:  # Ensure password was submitted
            return apology("must provide password", 403)

        session["user_id"] = username    # Remember which user has logged in

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear() # Forget any user_id
    return redirect("/")

@app.route("/quote")
@login_required
def quote():
    return render_template("quote.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/buy")
@login_required
def buy():
    return render_template("buy.html")

@app.route("/sell")
@login_required
def sell():
    return render_template("sell.html")

@app.route("/history")
@login_required
def history():
    return render_template("history.html")

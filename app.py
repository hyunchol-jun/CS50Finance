from flask import Flask, render_template, redirect, session, request, flash
from flask.helpers import get_flashed_messages
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology, lookup, usd

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

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create sqlite3 database connection 
connection = sqlite3.connect("finance.db", check_same_thread=False)
connection.isolation_level = None
cur = connection.cursor()

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

        user = cur.execute(
                "SELECT * FROM users WHERE (username = ?)", 
                [username]
            ).fetchone()
        hashChecked = check_password_hash(user[2], password)
        if user is None or not hashChecked:
            return apology("Invalid username and/or password", 403)
        
        session["user_id"] = username    # Remember which user has logged in

        return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear() # Forget any user_id
    return redirect("/")

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        if quote is None:   # Ensure the symbol was submitted
            return apology("Not a valid symbol", 400)
        else:
            return render_template(
                "quoted.html",
                name=quote["name"],
                symbol=quote["symbol"],
                price=quote["price"]
            )
    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        duplicateName = cur.execute(
                "SELECT * FROM users WHERE (username = ?)", [username]
            ).fetchone()

        if not username:
            return apology("must provide username", 400)
        elif duplicateName is not None:
            return apology("username already exists", 400)
        elif not confirmation:
            return apology("must confirm password", 400)
        elif not password == confirmation:
            return apology("passwords must match", 400)
        else:
            hash = generate_password_hash(
                    password, method="pbkdf2:sha256", salt_length=8
                    )
            cur.execute(
                    "INSERT INTO users (username, hash) VALUES (?, ?)",
                    [username, hash]
                    )
            connection.commit()

            return redirect("/")

    else:
        return render_template("register.html")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        quote = lookup(symbol)
        user_cash = 10000.00

        if not symbol or quote is None:
            return apology("Symbol not valid", 400)

        try:
            shares = int(shares)
            if shares < 1:
                return apology("Number of shares must be greater or equal to 1", 400)
        except ValueError:
            return apology("Number of shares must be a positive integer", 400)
            
        total_price = shares * quote["price"]
        
        if user_cash < total_price:
            return apology("You don't have sufficient cash", 400)
        else:
            flash("Transaction successful")
            return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "POST":
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        try:
            shares = int(shares)
            if shares < 1:
                return apology("Number of shares must be positive")
        except ValueError:
            return apology("Number of shares must be positive integer")
        if not symbol:
            return apology("missing symbol")
        stocks = 10;
        if shares > stocks:
            return apology("You don't have that many shares to sell")
        price = lookup(symbol)["price"]
        total_price = price * shares

        flash("Successfully sold!")
        return redirect("/")

        
    else:
        return render_template("sell.html")

@app.route("/history")
@login_required
def history():
    return render_template("history.html")

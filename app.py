from flask import Flask, render_template, redirect, session, request, flash
from flask.helpers import get_flashed_messages
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required, apology, lookup, usd
from models import *
from flask_sqlalchemy import SQLAlchemy
import os


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

# Configure sqlalchemy
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Create db tables
def main():
    db.create_all()

if __name__ == "__main__":
    with app.app_context():
        main()

@app.route("/")
@login_required
def index():
    user = session["user"]
    stocks = db.session.query(
            Stock.symbol, db.func.sum(Stock.shares)
            ).where(Stock.userID==user.id).group_by(Stock.symbol
                    ).having(db.func.sum(Stock.shares) > 0).all()
    stocksList = [{}]
    totalStockValue = 0.0
    for stock in stocks:
        stockDict = {}
        quote = lookup(stock[0])
        stockDict["symbol"] = stock[0]
        stockDict["shares"] = stock[1]
        stockDict["name"] = quote["name"]
        stockDict["price"] = quote["price"]
        stockDict["total"] = quote["price"] * stock[1]
        stocksList.append(stockDict)
        totalStockValue += stockDict["total"]

    totalCash = totalStockValue + user.cash
    return render_template(
            "index.html",
            stocks=stocksList,
            user_cash=user.cash,
            total_cash=totalCash
            )

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

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.hash, password):
            return apology("Invalid username and/or password", 403)
        
        session["user"] = user          # Remember which user has logged in

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
        
        duplicateName = User.query.filter_by(username=username).first()

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

            user = User(username=username, hash=hash)
            db.session.add(user)
            db.session.commit()

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
        user = session["user"]

        if not symbol or quote is None:
            return apology("Symbol not valid", 400)

        try:
            shares = int(shares)
            if shares < 1:
                return apology(
                        "Number of shares must be greater or equal to 1", 400)
        except ValueError:
            return apology("Number of shares must be a positive integer", 400)
            
        total_price = shares * quote["price"]
        
        if user.cash < total_price:
            return apology("You don't have sufficient fund", 400)
        else:
            user.cash = user.cash - total_price
            user.add_record(
                    symbol=symbol.upper(), shares=shares, price=quote["price"])
            flash("Transaction successful")
            return redirect("/")

    else:
        return render_template("buy.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    user = session["user"]

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
        numOfStocks = db.session.query(db.func.sum(Stock.shares)).where(
                        Stock.userID == user.id
                        and Stock.symbol == symbol).first()[0]
        if shares > numOfStocks:
            return apology("You don't have that many shares to sell")
        price = lookup(symbol)["price"]
        total_price = price * shares

        user.cash = user.cash + total_price
        user.add_record(
                symbol=symbol.upper(), shares=-shares, price=price)

        flash("Successfully sold!")
        return redirect("/")
    else:
        stocks = db.session.query(Stock.symbol, db.func.sum(Stock.shares)
                ).where(Stock.userID==user.id).group_by(Stock.symbol
                        ).having(db.func.sum(Stock.shares) > 0).all()
        return render_template("sell.html", stocks=stocks)

@app.route("/history")
@login_required
def history():
    user = session["user"]
    stocks = user.records[::-1]
    return render_template("history.html", stocks=stocks)

from flask import Flask, render_template, redirect
from flask_session import Session
from tempfile import mkdtemp

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
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return redirect("/")

@app.route("/quote")
def quote():
    return render_template("quote.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/buy")
def buy():
    return render_template("buy.html")

@app.route("/sell")
def sell():
    return render_template("sell.html")

@app.route("/history")
def history():
    return render_template("history.html")

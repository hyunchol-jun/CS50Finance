from flask import Flask, render_template, redirect

app = Flask(__name__)

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

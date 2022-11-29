import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd
#added this by myself, prints current date and time
#print(datetime.now()) Output: 2018-09-12 14:17:56.456080
from datetime import datetime
#just for trunc function
import math


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set

if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

#create history database with type(sell or buy)
db.execute("CREATE TABLE IF NOT EXISTS history(user_id INTEGER NOT NULL, symbol TEXT NOT NULL, shares INT NOT NULL, price FLOAT NOT NULL, totalprice FLOAT NOT NULL, type TEXT NOT NULL, time TEXT)")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#completed
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""
    #display symbol,shares, updatedprice{{lookup["price"]}}, totalprice for that purchase
    #updatedcash, total stock price
    allstocks = db.execute("SELECT * FROM buy where user_id = ?", session["user_id"])
    #symbol = row["symbol"]
    #shares = row["shares"]
    #updatedprice = lookup(row["symbol"])["price"]
    #totalprice = row["totalprice"]
    cash = db.execute("SELECT cash FROM users where id = ?", session["user_id"])
    #show cash with only 2 decimal points
    cash = usd(cash[0]["cash"])
    #cash = math.trunc(cash[0]["cash"] * 100)/100
    #totalstocksprice is required to be displayed in html
    totalstocksprice = 0
    for stock in allstocks:
        totalstocksprice = stock["totalprice"] + totalstocksprice
    return render_template("layout.html", allstocks=allstocks, cash=cash, totalstocksprice=math.trunc(totalstocksprice*100)/100)

#COMPLETED
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        #get symbol to look it up and number of shares the user wants
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Ensure symbol field isn't blank")
        elif not symbol.isalpha():
            return apology("Stock symbols can only contain alphabetical letters")
        dict = lookup(symbol)
        #check if symbol exists
        if dict == None:
            return apology("stock not found , please enter valid stock symbol")
        #if form's input isn't int or empty, return none
        shares = request.form.get("shares", type=int)
        #shares must be integer and positive
        if shares == None:
            return apology("shares must contain no letters and an integer")
        elif shares < 1:
            return apology("shares must be positive")
        totalprice = dict["price"] * shares
        #query for user's cash to see if it's more than the totalprice
        cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        #if the user does have enough money, buy and store the number of shares and price of share
        if cash >= totalprice:
            cash = cash - totalprice
            #put new cash in database
            db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])
            #create table in finance.db to save share's symbol and price
            db.execute("CREATE TABLE IF NOT EXISTS buy(user_id INTEGER NOT NULL, symbol TEXT NOT NULL, shares INT NOT NULL, price FLOAT NOT NULL, totalprice FLOAT NOT NULL)")
            #insert userid, symbol, shares, price, total price into table buy
            db.execute("INSERT INTO buy (user_id, symbol, shares, price, totalprice) VALUES(?, ?, ?, ?, ?)",session["user_id"], symbol, shares, dict["price"], totalprice)
            #attach to history
            db.execute("INSERT INTO history (user_id, symbol, shares, price, totalprice, type, time) VALUES(?, ?, ?, ?, ?, ?, ?)",session["user_id"], symbol, shares, dict["price"], totalprice, "BUY", datetime.now())
        else:
            return apology("Not enough cash available")
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    #will be displayed in html history
    history = db.execute("SELECT * FROM history WHERE user_id = ?", session["user_id"])
    #<td>{{ row["type"] }}</td>
    #<td>{{ row["symbol"] }}</td>
    #<td>{{ row["shares"] }}</td>
    #<td>{{ row["price"] }}</td>
    #<td>{{ row["totalprice"] }}</td>
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    #ask the user for a stock symbol and look it up and return its name and price
    if request.method == "POST":
        #this form is on quote.html
        symbol = request.form.get("symbol").upper()
        # symbol must be valid : contatin only alphabetical letters
        if not symbol:
            return apology("Ensure symbol field isn't blank")
        elif " " in symbol or not symbol.isalpha():
            return apology("Stock symbols can only contain alphabetical letters")
        dict = lookup(symbol)
        name = dict["name"]
        price = dict["price"]
        symbol = dict["symbol"]
        #if stock symbol wasn't found
        if dict == None:
            return apology("Stock not found , please enter valid stock symbol")
        #the resultes are displayed on a different html quoted.html
        return render_template("quoted.html",name=name, price=price, symbol=symbol)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #when requested via post, check for possible errors and insert the new user into users table and also log user in
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        #confirm if any field is blank or password and confirm password don't match or username is taken
        userexists = db.execute("SELECT username FROM users WHERE username = ?",username)
        if not username:
            return apology("username field is blank")
        elif not password:
            return apology("password field is blank")
        elif password != confirmation:
            return apology("passwords don't match , Please ensure both fields are the same")
        elif userexists:
            return apology("username is taken")
        #everthing is ok then register user
        else:
            #hash user's password to protect it (werkzeug library)
            hash = generate_password_hash(password)
            # add user to users table
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
            #TODO login user , might be login()  ???
            session["user_id"] = db.execute("SELECT * FROM users WHERE username = ?",username)[0]["id"]
            return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        shares = request.form.get("shares", type=int)
        symbol = request.form.get("symbol").upper()
        if not symbol:
            return apology("Please select a stock from the dropdown menu")
        elif shares < 1 or not shares:
            return apology("Please enter a positive integer for shares")
        stock = db.execute("SELECT * FROM buy WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
        #number of stocks he owns less than the shares he wants to sell
        if stock[0]["shares"] < shares:
            return apology("you don't own that many stocks")
        #sell is gonna go through
        else:
            #money he is gonna gain through selling this shares of stocks
            cashearned = stock[0]["shares"] * lookup(symbol)["price"]
            currentcash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            updatedcash = cashearned + currentcash
            db.execute("UPDATE users SET cash = ? WHERE id = ?", updatedcash, session["user_id"])
            newshares = stock[0]["shares"] - shares
            #update shares he has with the new number
            db.execute("UPDATE buy SET shares = ? WHERE user_id = ? AND symbol = ?", newshares, session["user_id"], symbol)
            #delete from buy the row with that stock
            #db.execute("DELETE FROM buy WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)
            #this is to attach to history
            db.execute("INSERT INTO history (user_id, symbol, shares, price, totalprice, type, time) VALUES(?, ?, ?, ?, ?, ?, ?)",session["user_id"], symbol, shares, lookup(symbol)["price"], cashearned, "SELL", datetime.now())
            return redirect("/")
    #GET
    else:
        jinjastock = db.execute("SELECT * FROM buy WHERE user_id = ?",session["user_id"])
        return render_template("sell.html", jinjastock=jinjastock)

#personal touch (ADD cash)
@app.route("/addcash",methods=["GET", "POST"])
@login_required
def addcash():
    if request.method == "POST":
        cashadded = request.form.get("cashadded", type=float)
        if not cashadded or cashadded < 0:
            return apology("must be positive number")
        else:
            cash = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            newcash = cash + cashadded
            db.execute("UPDATE users SET cash = ? WHERE id = ?", newcash, session["user_id"])
            return redirect("/")
    else:
        return render_template("addcash.html")

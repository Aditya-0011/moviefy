from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from tmdbv3api import TMDb, Movie, TV
import sqlite3
from hashlib import md5
from pprint import pprint


class User:
    username = None
    email = None
    password = None


conn = sqlite3.connect('Database.sqlite', check_same_thread=False)
cur = conn.cursor()

tmdb = TMDb()
tmdb.api_key = '0e5909614d58cec33516530e8b7b975b'
tmdb.language = 'en'
tmdb.debug = True

movie = Movie()

app = Flask(__name__)
uSer = User()


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].lower()
        password = request.form["password"]

        password = md5((password + username).encode()).hexdigest()
        cur.execute('''Select * From Users Where userName = ? And Password = ?''', (username, password))
        row = cur.fetchone()

        if row is not None:
            uSer.username = username
            return redirect("/" + username)
        else:
            return render_template("login.html")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username'].lower()
        email = request.form['email']
        password = request.form['password']

        if username == "login" or username == "signup":
            return render_template("signup.html")

        password = md5((password + username).encode()).hexdigest()
        try:
            cur.execute('''Insert Into Users (userName, Email, Password) Values( ?, ?, ? )''',
                        (username, email, password))
            conn.commit()
            cur.execute(f'''Create Table {username} (movieName Blob, movieId Integer,moviePath Blob);''')
            conn.commit()
            uSer.username = username
            return redirect("/" + username)

        except sqlite3.IntegrityError:
            return render_template("signup.html")

    return render_template("signup.html")


@app.route("/<name>", methods=["GET", "POST"])
def user(name):

    if request.method == "POST":
        Search = request.form['search']
        movies = movie.search(Search)
        l = []
        pprint(movies[0])

        for i in movies:
            l.append([i.title, i.id, "https://www.themoviedb.org/t/p/w600_and_h900_bestv2" + (i.backdrop_path or "")])

        return render_template("user.html", leng=len(l), b =l)

    # movies = movie.details(id)
    # print(movies.poster_path)
    # cur.execute(f'''Insert Into {access} (movieName, movieId, moviePath)
    #                 Values( ?, ?, ? )''', (movies.title, id, movies.poster_path))
    # conn.commit()
    # print("\n\tMovie added to wishlist.")
    # input("\n\tPress any key to continue.")
    # return Menu()
    else:
        try:
            cur.execute(f'''Select * From {name}''')
            row = cur.fetchall()
            a = []
            for movies in row:
                a.append(
                    [str(movies[0]), str(movies[1]),
                     "https://www.themoviedb.org/t/p/w600_and_h900_bestv2" + str(movies[2])])

            if uSer.username is None:
                return render_template("user.html", len=len(a), a=a, leng=0, b=[[]])

        except:
            return redirect(url_for("index"))

    return render_template("user.html", len=len(a), a=a, leng=0, b=[[]])


if __name__ == "__main__":
    app.run(host="", use_reloader=True, debug=True)

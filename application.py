import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
# Database uri postgres://kxtcnozmbccrfp:eeacaf63e2c0980c7d11c7fad11315d8df469b63e2f19883cb1cf4fee360cafe@ec2-18-210-214-86.compute-1.amazonaws.com:5432/dat261bh7u5jtg

# if not os.getenv("DATABASE_URL"):
#     raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://kxtcnozmbccrfp:eeacaf63e2c0980c7d11c7fad11315d8df469b63e2f19883cb1cf4fee360cafe@ec2-18-210-214-86.compute-1.amazonaws.com:5432/dat261bh7u5jtg")
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if 'name' in session:
        name = session['name']
        status = True
        return render_template("index.html", name=name)
    return render_template("index.html")

# User auths

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        if 'name' in session:
            return render_template("logout.html")
        return render_template("signup.html")

    name = request.form.get('name')
    password = request.form.get('password')

    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)", {"name": name, "password": password})
    db.commit()

    return redirect(url_for("login"))
    
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if 'name' in session:
            return render_template("logout.html")
        return render_template("login.html")
    
    name = request.form.get('name')
    password = request.form.get('password')

    user_data = db.execute("SELECT * FROM users WHERE name = :name", {"name": name}).fetchone()

    if name == user_data.name and password == user_data.password:
        session['name'] = user_data.name
        return redirect(url_for("index"))
    else:
        return "Username does not match"


@app.route("/logout", methods=['POST'])
def logout():
    session.pop('name', None)
    return redirect(url_for("index"))

# End USER auths

# Returning search results after the user

@app.route("/search", methods=['POST'])
def search():
    search = request.form.get('search')
    search_by = request.form.get('search-by')
    if search_by == 'isbn':
        results = db.execute("SELECT * FROM books WHERE isbn ~* :isbn", {"isbn": search}).fetchall()
        print(results)
        return render_template("result.html", results=results)
    elif search_by == 'title':
        results = db.execute("SELECT * FROM books WHERE title ~* :title", {"title": search}).fetchall()
        return render_template("result.html", results=results)
    elif search_by == 'author':
        results = db.execute("SELECT * FROM books WHERE author ~* :author", {"author": search}).fetchall()
        return render_template("result.html", results=results)
    elif search_by == 'year':
        results = db.execute("SELECT * FROM books WHERE pub_year = :year", {"year": int(search)}).fetchall()
        return render_template("result.html", results=results)


# Route for details Aboute specif book


@app.route("/details", methods=["GET", "POST"])
def details():
    if request.method == "GET":
        isbn = request.args.get("isbn")
        if 'name' in session:
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
            reviews = db.execute("SELECT reviews, name FROM reviews JOIN users ON reviews.user_id = users.id WHERE reviews.book_id = :isbn", {"isbn":isbn})
            return render_template("details.html", book=book, reviews=reviews, isbn=isbn)
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
        reviews = db.execute("SELECT reviews, name FROM reviews JOIN users ON reviews.user_id = users.id WHERE reviews.book_id = :isbn", {"isbn":isbn})
        return render_template("details.html", book=book, reviews=reviews)
    
    # Review of the user
    user = db.execute("SELECT * FROM users WHERE name = :name", {"name":session['name']}).fetchone()

    if db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :isbn", {"user_id":user.id, "isbn":isbn}).rowcount != 0:
        return "User already added a review"



    comment = request.form.get('comment')
    new_rating = int(request.form.get('rating'))
    

    db.execute("INSERT INTO reviews (user_id, book_id, reviews) VALUES (:user_id, :book_id, :reviews)", {"user_id": user.id, "book_id": isbn, "reviews":comment})
    db.commit()

    db.execute("UPDATE books SET rating_val = rating_val + 1 WHERE isbn = :isbn AND rating_val < 2", {"isbn":isbn})
    db.commit()

    db.execute(f"UPDATE books SET rating = ((rating + {new_rating})/rating_val) WHERE isbn = :isbn", {"isbn":isbn})
    db.commit()

    return redirect(url_for("details", isbn=isbn))

if __name__ == "__main__":
    app.run(debug=True)
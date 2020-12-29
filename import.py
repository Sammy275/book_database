import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://kxtcnozmbccrfp:eeacaf63e2c0980c7d11c7fad11315d8df469b63e2f19883cb1cf4fee360cafe@ec2-18-210-214-86.compute-1.amazonaws.com:5432/dat261bh7u5jtg")
db = scoped_session(sessionmaker(bind=engine))

with open("books1.csv", 'r') as file:
    books = csv.DictReader(file)
    for book in books:
        isbn = book['isbn']
        title = book['title']
        author = book['author']
        year = int(book['year'])
        rating = int(book['rating'])
        rating_val = int(book['rating_val'])
        db.execute("INSERT INTO books (isbn, title, author, pub_year, rating, rating_val) VALUES (:isbn, :title, :author, :pub_year, :rating, :rating_val)", {"isbn":isbn, "title":title, "author":author, "pub_year":year, "rating":rating, "rating_val":rating})
        db.commit()

# db.execute("INSERT INTO books (isbn, title, author, pub_year, rating, rating_val) VALUES (:isbn, :title, :author, :pub_year, :rating, :rating_val)", {"isbn":"380795272", "title":"Krondor: The Betrayal", "author":"Raymond E. Feist", "pub_year":1998, "rating":0, "rating_val":0})
# db.commit()
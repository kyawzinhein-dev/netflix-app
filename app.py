# Netflix Flask CRUD application
from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)

def db_conn():
    conn = sqlite3.connect('netflix.db')        #connect to database
    conn.row_factory = sqlite3.Row              #Format to list 
    return conn

def create_movies_table():
    db = db_conn()

    db.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT,
            category TEXT,
            release_year INT,
            rating REAL,
            description TEXT,
            poster TEXT
        )
    """)

    db.commit()
    db.close()

@app.route('/')        #index.html home
def home():

    db = db_conn()
    movies = db.execute('SELECT * FROM movies').fetchall()
    db.close()


    #movies = []

    # movies = [
    # {"title" : "Spider-Man", "category" : "Fantasy"},
    # {"title" : "Titanic", "category" : "Dramma"}
    # ]
    return render_template('index.html', movies=movies) #key = variable

@app.route('/movies', methods=['GET', 'POST'])   #movie.html
def movies():
    if request.method == 'POST':
       title = request.form['title']
       category = request.form['category']
       release_year = request.form['release_year']
       rating = request.form['rating']
       description = request.form['description']

       poster = request.files['poster']
       poster_name = poster.filename                                #name -> database
       poster.save('static/uploads/' + poster_name)                 #image object -> static

       db = db_conn()
       db.execute(
           "INSERT INTO movies (title, category, release_year, rating, description, poster) VALUES (?, ?, ?, ?, ?, ?)",
           (title, category, release_year, rating, description, poster_name,)
       )
       db.commit()
       db.close()

       return redirect('/')


    db = db_conn()
    movies = db.execute('SELECT * FROM movies').fetchall()
    db.close()
    return render_template('movies.html', movies = movies)

@app.route('/movies/edit/<int:id>', methods=['GET', 'POST'])    #edit
def edit_movie(id):

    db = db_conn()
    movie = db.execute('SELECT * FROM movies WHERE id = ?',(id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        release_year = request.form['release_year']
        rating = request.form['rating']
        description = request.form['description']
        poster = request.files['poster']

        if poster and poster.filename:
            poster_name = poster.filename
            poster.save('static/uploads/' + poster_name)

            db.execute(
                '''
                UPDATE movies
                SET title = ?, category = ?, release_year = ?, rating = ?,
                    description = ?, poster = ?
                WHERE id = ?
                ''',
                (title, category, release_year, rating,
                description, poster_name, id)
            )
        else:
            db.execute(
                '''
                UPDATE movies
                SET title = ?, category = ?, release_year = ?, rating = ?,
                    description = ?
                WHERE id = ?
                ''',
                (title, category, release_year, rating,
                description, id)
            )

        db.commit()
        db.close()

        return redirect('/movies')

    db.close()

    return render_template('edit.html', movie=movie)

@app.route('/movies/delete/<int:id>')           #delete
def delete_movie(id):

    db = db_conn()

    movie = db.execute(
        'SELECT * FROM movies WHERE id = ?',
        (id,)
    ).fetchone()

    poster_name = movie['poster']
    poster_path = 'static/uploads/' + poster_name

    if os.path.exists(poster_path):
        os.remove(poster_path)

    db.execute(
        'DELETE FROM movies WHERE id = ?',
        (id,)
    )

    db.commit()
    db.close()

    return redirect('/movies')

@app.route('/movies/create')    #create.html
def create():
    return render_template('create.html')

if __name__ == '__main__':
    create_movies_table()
    app.run(host="127.0.0.1", port = "8080", debug = True)

from setup import setup, query
from flask import Flask, render_template, request, url_for, redirect
import threading, time

# Setup the BM25 scorer so that we can call the query function
# This is called before setting up the server because we want to be
# able to quickly query the data. The initial setup takes the longest.
# setup()

application = Flask(__name__)


@application.route("/")
def index():
    return render_template("index.html")


@application.route("/find", methods=["GET", "POST"])
def find():
    output = []
    if request.method == "POST":
        # Gets textbox words and stores them in this variable
        user_query = request.form[
            "query_text"
        ].lower()  # You will see name="query_text" at our form's textbox on find.html

        # Returns pandas dataframe with COLS and n rows
        retrieved_songs = query(user_query, 5)

        for row in retrieved_songs.itertuples():
            output.append( [row.SONG_NAME.title(), row.ARTIST_NAME.title()] )
            print(row.SONG_NAME)
            print(row.ARTIST_NAME)
    return render_template("find.html", outputtext=output)

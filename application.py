from multiprocessing import context
from setup import setup, query
from flask import Flask, render_template, request, url_for, redirect

# Setup the BM25 scorer so that we can call the query function
# This is called before setting up the server because we want to be
# able to quickly query the data. The initial setup takes the longest.
setup()

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
        retrieved_songs = query(user_query, 12)

        for row in retrieved_songs.itertuples():
            lyrics = row.LYRICS.title().lower()
            # freq = [lyrics.count(word) for word in user_query.split()] # Make frequency list for words in query
            # index_min = max(range(len(freq)), key=freq.__getitem__) # trick for idx from min function
            # infreq_word = user_query.split()[index_min] # The least frequent word in the query
            # contextidx = lyrics.find(infreq_word)
            # context = ' '.join(lyrics.split()[contextidx-1 : contextidx+2]) # Small chance this error is out because the least frequent word appears at the end of the song

            context = ' '.join(lyrics.split()[:10])
            output.append( [row.SONG_NAME.title(), row.ARTIST_NAME.title(), context] )
            print(row.SONG_NAME)
            print(row.ARTIST_NAME)
    return render_template("find.html", outputtext=output)

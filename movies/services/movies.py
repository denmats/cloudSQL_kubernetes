from tools import root_dir, nice_json
from flask import Flask
from werkzeug.exceptions import NotFound
import json
import collections
import mysql.connector
import os

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "movies": "/movies",
            "movie": "/movies/<id>"
        }
    })

@app.route("/movies/<movieid>", methods=['GET'])
def movie_info(movieid):
    db = mysql.connector.connect(
        host="127.0.0.1",
        user='proxyuser',
        password='123',
        database="mydb"
    )
    cur = db.cursor()
    cur.execute('SELECT id FROM movies WHERE id = "{}"'.format(movieid))
    data_to_read = cur.fetchall()
    if data_to_read == []:
        db.close()
        raise NotFound

    cur.execute('SELECT * FROM movies WHERE id = "{}"'.format(movieid))
    data_to_read = cur.fetchall()
    db.close()
    rowarray_list = {}
    for row in data_to_read:
        d = collections.OrderedDict()
        d['title'] = row[0]
        d['rating'] = row[1]
        d['director'] = row[2]
        d['id'] = row[3]
        rowarray_list[d['id']] = d

    j = json.dumps(d, indent = 4, sort_keys = True) 
    parsed = json.loads(j)
    parsed["uri"] = "/movies/{}".format(movieid)
    return nice_json(parsed)


@app.route("/movies", methods=['GET'])
def movie_record():
    db = mysql.connector.connect(
        host="127.0.0.1",
        user='proxyuser',
        password='123',
        database="mydb"
    )
    cur = db.cursor()
    cur.execute("SELECT * FROM movies")
    data_to_read = cur.fetchall()
    rowarray_list = {}
    for row in data_to_read:
        d = collections.OrderedDict()
        d['title'] = row[0]
        d['rating'] = row[1]
        d['director'] = row[2]
        d['id'] = row[3]
        rowarray_list[d['id']] = d

    j = json.dumps(rowarray_list, indent = 4, sort_keys = True) 
    parsed = json.loads(j)
    return nice_json(parsed)


if __name__ == "__main__":
    app.run(host= "0.0.0.0", port=8080, debug=True)

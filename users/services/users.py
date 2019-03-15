from tools import root_dir, nice_json
from flask import Flask
from werkzeug.exceptions import NotFound, ServiceUnavailable
import json
import requests
import collections
import mysql.connector
import os


app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "users": "/users",
            "user": "/users/<username>",
            "bookings": "/users/<username>/bookings",
            "suggested": "/users/<username>/suggested"
        }
    })


@app.route("/users", methods=['GET'])
def users_list():
    db = mysql.connector.connect(
        host='127.0.0.1',
        user='proxyuser',
        password='123',
        database='mydb'
    )
    cur = db.cursor()
    cur.execute("SELECT * FROM users")
    data_to_read = cur.fetchall()
    db.close()
    rowarray_list = {}
    for row in data_to_read:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['name'] = row[1]
        d['last_active'] = row[2]
        rowarray_list[d['id']] = d

    j = json.dumps(rowarray_list, indent = 4, sort_keys = True) 
    parsed = json.loads(j)
    return nice_json(parsed)


@app.route("/users/<username>", methods=['GET'])
def user_record(username):
    db = mysql.connector.connect(
        host='127.0.0.1',
        user='proxyuser',
        password='123',
        database='mydb'
    )
    cur = db.cursor()
    cur.execute('SELECT id FROM users WHERE id = "{}"'.format(username))
    data_to_read = cur.fetchall()
    if data_to_read == []:
        db1.close()
        raise NotFound

    cur.execute('SELECT * FROM users WHERE id = "{}"'.format(username))
    data_to_read = cur.fetchall()
    db.close()
    rowarray_list = {}
    for row in data_to_read:
        d = collections.OrderedDict()
        d['id'] = row[0]
        d['name'] = row[1]
        d['last_active'] = row[2]
        rowarray_list[d['id']] = d

    j = json.dumps(rowarray_list, indent = 4, sort_keys = True) 
    parsed = json.loads(j)
    return nice_json(parsed)


@app.route("/users/<username>/bookings", methods=['GET'])
def user_bookings(username):
    """
    Gets booking information from the 'Bookings Service' for the user, and
     movie ratings etc. from the 'Movie Service' and returns a list.
    :param username:
    :return: List of Users bookings
    """
    db = mysql.connector.connect(
        host="127.0.0.1",
        user='proxyuser',
        password='123',
        database="mydb"
    )
    cur = db.cursor()
    cur.execute('SELECT id FROM users WHERE id = "{}"'.format(username))
    data_to_read = cur.fetchall()
    db.close()
    if data_to_read == []:
        raise NotFound("User '{}' not found.".format(username))

    try:
        users_bookings = requests.get("http://bookings-service:8080/bookings/{}".format(username))
    except requests.exceptions.ConnectionError:
        raise ServiceUnavailable("The Bookings service is unavailable.")

    if users_bookings.status_code == 404:
        raise NotFound("No bookings were found for {}".format(username))

    users_bookings = users_bookings.json()

    # For each booking, get the rating and the movie title
    result = {}
    for date, movies in users_bookings.items():
        result[date] = []
        for movieid in movies:
            try:
                movies_resp = requests.get("http://movies-service:8080/movies/{}".format(movieid))
            except requests.exceptions.ConnectionError:
                raise ServiceUnavailable("The Movie service is unavailable.")
            movies_resp = movies_resp.json()
            result[date].append({
                "title": movies_resp["title"],
                "rating": movies_resp["rating"],
                "uri": movies_resp["uri"]
            })

    return nice_json(result)


@app.route("/users/<username>/suggested", methods=['GET'])
def user_suggested(username):
    """
    Returns movie suggestions. The algorithm returns a list of 3 top ranked
    movies that the user has not yet booked.
    :param username:
    :return: Suggested movies
    """
    raise NotImplementedError()


if __name__ == "__main__":
    app.run(host= '0.0.0.0', port=8080, debug=True)

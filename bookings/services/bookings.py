from tools import root_dir, nice_json
from flask import Flask
import json
from werkzeug.exceptions import NotFound
import collections
import mysql.connector
import os

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello():
    return nice_json({
        "uri": "/",
        "subresource_uris": {
            "bookings": "/bookings",
            "booking": "/bookings/<username>"
        }
    })


@app.route("/bookings", methods=['GET'])
def booking_list():
    db = mysql.connector.connect(
        host="127.0.0.1",
        user='proxyuser',
        password='123',
        database="mydb"
    )
    cur = db.cursor()
    cur.execute("SELECT * FROM bookings")
    data_to_read = cur.fetchall()
    db.close()
    rowarray_list = {}
    for row in data_to_read:
        t = row[1]
        if row[0] not in rowarray_list:
            rowarray_list[row[0]] = {}

        if row[1] not in rowarray_list[row[0]].keys():
            rowarray_list[row[0]][row[1]] = []

        rowarray_list[row[0]][row[1]].append(row[2])

    j = json.dumps(rowarray_list, indent = 4, sort_keys = True)
    parsed = json.loads(j)
    return nice_json(parsed)


@app.route("/bookings/<username>", methods=['GET'])
def booking_record(username):
    db = mysql.connector.connect(
        host="127.0.0.1",
        user='proxyuser',
        password='123',
        database="mydb"
    )
    cur = db.cursor()
    cur.execute('SELECT id FROM bookings WHERE id = "{}"'.format(username))
    data_to_read = cur.fetchall()
    if data_to_read == []:
        db.close()
        raise NotFound

    cur.execute('SELECT * FROM bookings WHERE id = "{}"'.format(username))
    data_to_read = cur.fetchall()
    db.close()
    rowarray_list = {}
    for row in data_to_read:
        t = row[2]
        if row[1] not in rowarray_list:
            rowarray_list[row[1]] = []

        rowarray_list[row[1]].append(t)

    j = json.dumps(rowarray_list, indent = 4, sort_keys = True) 
    parsed = json.loads(j)
    return nice_json(parsed)


if __name__ == "__main__":
    app.run(host= "0.0.0.0", port=8080, debug=True)


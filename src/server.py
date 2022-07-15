#!/usr/bin/python3

import random
import string
import hashlib
import pymongo

from flask import Flask , render_template , request

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('home.html')

@app.route("/users/add",methods=["POST"])
def adduser():
    payload = request.get_json(force=True)
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["SummerTalk"]
    coll = db["users"]
    if coll.find_one({"username":payload["username"]}):
        return "Username already taken!"
    hashed_pass = hashlib.sha256(payload["password"].encode("utf-8")).hexdigest()
    added_user = coll.insert_one({"username":payload["username"],"password":hashed_pass})
    return "User created with token {}".format(added_user.inserted_id)         

if __name__ == "__main__":
    app.run(debug=True)    
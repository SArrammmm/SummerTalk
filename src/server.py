#!/usr/bin/python3

import json
import random
import string
import hashlib
import pymongo
import datetime

from flask import Flask , render_template , request , jsonify
from bson.objectid import ObjectId
from bson.json_util import dumps , loads

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

@app.route("/users/login",methods=["POST"])
def login():
    payload = request.get_json(force=True)
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["SummerTalk"]
    coll = db["users"]
    user = coll.find_one({"username":payload["username"]})
    if not user:
        return "No user found with such criteria"
    if user["password"] == hashlib.sha256(payload["password"].encode("utf-8")).hexdigest():
        return "Authentication successful! Token : {}".format(user["_id"])
    else:
        return "Authentication failed due to incorrect credentials"

@app.route("/inbox/add",methods=["POST"])
def send_message():
    payload = request.get_json(force=True)
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["SummerTalk"]
    inbox_coll = db["inbox"]
    users_coll = db["users"]
    user = users_coll.find_one({"_id" : ObjectId(payload["token"])}) 
    if not user:
        return "No user found with associated token"
    if not users_coll.find_one({"username":payload["To"]}):
        return "recipient does not exist"    
    msg_doc = {"To" : payload["To"],"From":user["username"],"message":payload["message"],"timestamp":datetime.datetime.utcnow()}
    msg_id = inbox_coll.insert_one(msg_doc).inserted_id
    return "Message sent successfully with ID {}".format(msg_id)

@app.route("/inbox/get",methods=["POST"])
def get_message():
    payload = request.get_json(force=True)
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client["SummerTalk"]
    inbox_coll = db["inbox"]
    users_coll = db["users"]
    user = users_coll.find_one({"_id" : ObjectId(payload["token"])}) 
    if not user:
        return "No user found with associated token"
    user_messages = inbox_coll.find({"To" : {"$eq" : user["username"]}})
    result = {"messages" : []}
    for message in user_messages:
        result["messages"].append(dumps(message))  
    return jsonify(result)    
          
if __name__ == "__main__":
    app.run(debug=True)    
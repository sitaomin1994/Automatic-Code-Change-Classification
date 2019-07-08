from pymongo import MongoClient
import json
from os import path
import os
import pprint


def readFiles(file_name):
    if path.exists(file_name):
        with open(file_name) as obj:
            output = json.load(obj)
            return output
    else:
        print("No such file: ", file_name)
        exit(-1)

def create_db():
    client = MongoClient("localhost", 27017)
    user_db = client["test_jsonDB"]
    coll = user_db["commit_hist"]
    pwd = os.getcwd()
    filename = pwd + "/68251383aa6ca0842ab5597fcf2f26c5a5b77aba.json"
    user_file = readFiles(filename)
    coll.insert_one(user_file)
    client.close()


def print_insertion():
    client = MongoClient("localhost", 27017)
    user_db = client.test_jsonDB
    commit_hist = user_db.commit_hist
    pprint.pprint(commit_hist.find_one())
    client.close()


create_db()
##print_insertion()
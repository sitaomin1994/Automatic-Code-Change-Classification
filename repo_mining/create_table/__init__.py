import pandas as pd
import psycopg2
from extract_commit_history import ExtractHistory
import os
from os import path
import subprocess
from pymongo import MongoClient
import json
import pprint

class CreateTable():
    def __init__(self, dbname, user, passwd, host):
        self.dbname = dbname
        self.user = user
        self.passwd = passwd
        self.host = host
        self.new_table = ""
        self.new_db = ""

    def get_commits_df(self):
        conn = None
        try:
            print("connecting to ...", self.dbname)
            conn = psycopg2.connect("dbname='{}' user='{}' password='{}' host='{}'".format \
                                        (self.dbname, self.user, self.passwd, self.host))
            df = pd.read_sql("SELECT application, csha FROM commits", conn)
            df_dict = dict()
            for application, sha in zip(df["application"].values, df["csha"].values):
                if df_dict.get(application) is None:
                    df_dict[application] = []
                df_dict[application].append(sha)
            conn.commit()
            return df_dict
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
        finally:
            if conn is not None:
                conn.close()

    def mine_repo(self):
        df_dict = self.get_commits_df()
        pwd = os.getcwd()
        json_dir = pwd + "/tmp_JSON"
        json_files = os.listdir(json_dir)
        for application, id_list in df_dict.items():
            for id in id_list:
                id_name = application + "_" + id + ".json"
                if id_name not in json_files:
                    extractor = ExtractHistory(application, id)
                    extractor.clone()
            self.delete_repo(application)

    def delete_repo(self, repo_name):
        pwd = os.getcwd()
        all_files = pwd + "/repos/" + repo_name
        cmd = ["rm", "-rf", all_files]
        if path.exists(all_files):
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

    def create_db(self, newdB, newCollection):
        self.new_db = self.new_db + newdB
        self.new_table = self.new_table + newCollection
        client = MongoClient("localhost", 27017)
        user_db = client[self.new_db]
        coll = user_db[self.new_table]
        pwd = os.getcwd()
        json_files = os.listdir(pwd + "/tmp_JSON")
        for json_file in json_files:
            with open(json_file) as f:
                data = json.load(f)
                coll.insert_one(data)
        client.close()
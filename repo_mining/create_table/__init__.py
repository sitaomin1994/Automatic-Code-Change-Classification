import os
from os import path
import subprocess
from pymongo import MongoClient
import asyncio
import json
import psycopg2
import pandas as pd
from extract_commit_history import ExtractHistory
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
            df = pd.read_sql("SELECT application, csha FROM commits WHERE csha <> 'c3f90581522d85a5e012690fad32f44939acd4a0'", conn)
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
        json_files.sort()
        loop = asyncio.get_event_loop()
        for application, id_list in df_dict.items():
            for id in id_list:
                id_name = application + "_" + id + ".json"
                if not self.search_dir(json_files, id_name):
                    try:
                        extractor = ExtractHistory(application, id)
                        loop.run_until_complete(extractor.clone())
                    except UnicodeEncodeError: 
                        print("unicode error detected in ... ", id_name)
                        with open("unicode_error_commits.txt", "a") as f: 
                            f.write(id_name)
                        continue
        
        
            self.delete_repo(application)

    def search_dir(self, tmp_dir, dir):
        first = 0
        last = len(tmp_dir) - 1
        found = False
        while first <= last and not found:
            midpoint = first + (last - first)//2
            if dir == tmp_dir[midpoint]:
                found = True
            else:
                if dir < tmp_dir[midpoint]:
                    last = midpoint - 1
                else:
                    first = midpoint + 1
        return found

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
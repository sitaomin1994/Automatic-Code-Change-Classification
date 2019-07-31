import pandas as pd 
import numpy as np 
import os
import json 
## Changing tags 
## Creating tags 
## writing to csv 
## looking up tags 
## prelabeling

class Tagger(): 

	def writing_to_csv(self, df, filename): 
		if os.path.exists(filename): 
			os.remove(filename)
		df.to_csv(filename, index=False)

	def prelabeling(self, df, filename, prelabels): 
		"""
		   :param df: Current DataFrame
		   :param filename: Filename for the keys words dictionary 
		   :param prelabels: list of labels in the dictionary that you want to name 
		   :return A prelabeled DataFrame 
		"""

		with open(filename, "r") as f: 
			labels = json.load(f)

		for prelabel in prelabels: 
			if not prelabel in df.columns: 
				df[prelabel] = 0 

		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get("check") is None: 
			df["check"] = "nc"
			col = dict()
			for idx, column in enumerate(df.columns): 
				col[column] = idx

		for row, message in enumerate(df["commit message"]):
			if df.iloc[row, col["check"]] != "c": 
				for prelabel in prelabels: 
					for keywords in labels[prelabel][0]: 
						for keyword in keywords:
							try:
								if keyword in message.split():
									df.iloc[row, col[prelabel]] = 1
									break
							except AttributeError as e: 
								continue 
		return df

	def get_commit(self, df, prelabel, label, tagger_id):
		"""

		   :param df: Current DataFrame
		   :param filename: Filename for the keys words dictionary 
		   :param prelabels: label in the dictionary that you want to name
		   :param lable: Either 1 or 0, this is the label you can the commit for 
		   :param tagger_id: unique tagger id ["jc": Jincheng, "kc": Kelechi, "jy": Jinying]
		   :return prints commit link of a random csha with specified prelabel and label and tagger_id  
		"""

		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get(prelabel) is None: 
			return 

		if col.get("commit link") is None: 
			org = df["Commit ID"].str.split("-").str[0]
			app = df["Commit ID"].str.split("-", 1).str[1].str.split("_").str[0]
			link = "https://github.com/" + org + "/" + app + "/commit/" + df["csha"]
			df["commit link"] = link 

		for row, commit_link in enumerate(df["commit link"]):
			if df.iloc[row, col["check"]] == "nc" and df.iloc[row, col[prelabel]] == label and df.iloc[row, col["Tagger ID"]] == tagger_id:
				return commit_link

	def label(self, df, label_name, csha, label):
		"""

		   :param df: Current DataFrame
		   :param label_name: name of a tag
		   :param chsa: commit sha 
		   :param label: Either 1 or 0, this is the label you can the commit for 
		   :return dataframe with sha labeled as label  
		"""
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get(label_name) is None: 
			df[label_name] = 0
			col = dict()
			for idx, column in enumerate(df.columns): 
				col[column] = idx

		row = df[df['csha'] == csha].index.tolist()[0]

		df.iloc[row, col[label_name]] = label

		return df

	def check(self, df, csha): 
		"""
        :param df: Current DataFrame
        :param csha: commit sha 
        :return DataFrame with the check column set to 'c'
		"""
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get("check") is None: 
			df[check] = "nc"

		row = df[df['csha'] == csha].index.tolist()[0]
		df.iloc[row, col["check"]] = "c"
		return df

	def uncheck(self, df, csha):
		"""
        :param df: Current DataFrame
        :param csha: commit sha 
        :return DataFrame with the check column set to 'nc'
		"""
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get("check") is None: 
			df["check"] = "nc"
			return 

		row = df[df['csha'] == csha].index.tolist()[0]
		df.iloc[row, col["check"]] = "nc"
		return df

	def getlabels(self, df, csha):
		
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		row = df[df['csha'] == csha].index.tolist()[0]
		
		for key in col.keys(): 
			if df.iloc[row, col[key]] == 1 and key not in ["deleted_files", "total_files"]: 
				print(key)



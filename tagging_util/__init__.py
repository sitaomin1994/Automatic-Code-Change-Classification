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

		for row, message in enumerate(df["commit message"]):
			if df.iloc[row, col["check"]] != "c": 
				for prelabel in prelabels: 
					for keyword in labels[prelabel][0]: 
						if keyword in message: 
							df.iloc[row, col[prelabel]] = 1
							break
		return df

	def get_commit(self, df, prelabel):
		"""

		   :param df: Current DataFrame
		   :param filename: Filename for the keys words dictionary 
		   :param prelabels: label in the dictionary that you want to name 
		"""

		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get(prelabel) is None: 
			return 

		for row, commit_link in enumerate(df["commit link"]): 
			if df.iloc[row, col["check"]] == "c": 
				continue 
			else:
				if df.iloc[row, col[prelabel]] is 0: 
					yield commit_link 
	def label(self, df, label_name, csha, label):

		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get(label) is None: 
			df[label] = 0

		row = df[df['csha'] == csha].index.tolist()[0]

		df.iloc[row, col[label_name]] = label

		return df

	def check(self, df, csha): 
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get("check") is None: 
			df[check] = "nc"

		row = df[df['csha'] == csha].index.tolist()[0]
		df.iloc[row, col["check"]] = "c"
		return df

	def uncheck(self, df, csha):
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		if col.get("check") is None: 
			df[check] = "nc"
			return 

		row = df[df['csha'] == csha].index.tolist()[0]
		df.iloc[row, col["check"]] = "nc"
		return df

	def getlabels(self, csha): 
		col = dict()
		for idx, column in enumerate(df.columns): 
			col[column] = idx

		row = df[df['csha'] == csha].index.tolist()[0]
		
		for key in col.keys(): 
			if df.iloc[row, col[key]] == 1 and key not in ["deleted_files", "total_files"]: 
				print(key)



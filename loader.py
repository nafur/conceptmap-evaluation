import csv
import glob
import os.path
import re

import database

FILE_PATTERN = {
	"default": ".*/?(?P<timing>(Vorher|Nachher))/.*_(?P<medium>(Video|Text))_(?P<ordering>[0-9]+)/(?P<trial>.*)-(?P<student>[^-]*)_[0-9]*\.csv"
}

def parseFilename(filename, pattern):
	res = re.match(FILE_PATTERN[pattern], filename)
	if res != None:
		trial = database.addTrial(res.group("trial"))
		student = database.addStudent(res.group("medium"), res.group("student"))
		solution = database.addSolution(student, res.group("ordering"), trial, res.group("timing"))
		return (trial,student,solution)
	print("Could not match \"" + filename + "\" against pattern \"" + FILE_PATTERN[pattern] + "\".")

def loadCSV(filename):
	file = open(filename, "r")
	reader = csv.DictReader(file, delimiter=";")
	return list(reader)

class NodeMap:
	def __init__(self,trial):
		self._m = {}
		self._trial = trial
	def get(self, name):
		if name in self._m:
			return self._m[name]
		id = database.addNode(self._trial,name)
		self._m[name] = id
		return id

def loadAnswerSet(path, pattern = "default"):
	database.open()
	if os.path.isfile(path):
		files = [path]
	elif os.path.isdir(path):
		files = glob.glob(path + "/*/*/*")
	else:
		print("\"" + path + "\" is neither a file nor a folder. We assume that it is a file pattern...")
		files = glob.glob(path)

	for file in files:
		print("Looking at " + file)
		(trial,student,solution) = parseFilename(file, pattern)
		history = loadCSV(file)
		n = 1
		nm = NodeMap(trial)
		data = {}
		for row in history:
			src = nm.get(row["Source"])
			dst = nm.get(row["Destination"])
			if row["Action"] == "Connecting":
				database.addProgress(solution, n, "create", src, dst, "")
				data[(src,dst)] = (n, "")
			elif row["Action"] == "Renaming":
				database.addProgress(solution, n, "rename", src, dst, row["to"])
				data[(src,dst)] = (n, row["to"])
			elif row["Action"] == "Disconnecting":
				database.addProgress(solution, n, "remove", src, dst, "")
				del data[(src,dst)]
			n += 1
		for d in data:
			ordering,desc = data[d]
			database.addAnswer(solution, ordering, d[0], d[1], desc)

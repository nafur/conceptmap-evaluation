import os.path
import sqlite3
import sys

DBCONN = None
DBFILE = "db.sqlite"
VERIFICATION_FLAGS = ["verified", "formal", "inhaltlich", "strukturell", "funktional"]

def open(filename = DBFILE):
	global DBCONN
	if DBCONN == None:
		DBCONN = sqlite3.connect(filename)
		DBCONN.row_factory = sqlite3.Row

def close():
	global DBOCNN
	if DBCONN != None:
		DBCONN.close()

def conn():
	global DBCONN
	return DBCONN

def cursor():
	global DBCONN
	return DBCONN.cursor()

def init(filename = DBFILE):
	if os.path.isfile(filename):
		print("Database \"" + filename + "\" already exists. Please remove it first...")
		sys.exit(1)
	open(filename)
	conn().execute('''CREATE TABLE trials (id integer primary key, name text)''')
	conn().execute('''CREATE TABLE nodes (id integer primary key, trial int, name text)''')
	conn().execute('''CREATE TABLE students (id integer primary key, medium text, name text)''')
	conn().execute('''CREATE TABLE solutions (id integer primary key, student int, ordering int, trial int, timing int)''')
	conn().execute('''CREATE TABLE answers (id integer primary key, solution int, ordering int, src int, dest int, description text, verification int DEFAULT 0)''')
	conn().execute('''CREATE UNIQUE INDEX answers_unique ON answers(solution,src,dest)''')
	conn().execute('''CREATE TABLE progress (id integer primary key, solution int, ordering int, action int, src int, dest int, description text, verification int DEFAULT 0)''')
	conn().execute('''CREATE UNIQUE INDEX progress_unique ON progress(solution,ordering)''')

def addTrial(name):
	c = cursor()
	c.execute("SELECT id FROM trials WHERE name LIKE ?", (name,))
	res = c.fetchone()
	if res != None:
		return res[0]
	with conn():
		c.execute("INSERT INTO trials (name) VALUES (?)", (name,))
	return c.lastrowid

def getTrial(id):
	return cursor().execute("SELECT * FROM trials WHERE id=?", (id,)).fetchone()

def listTrials():
	return cursor().execute("SELECT * FROM trials ORDER BY name").fetchall()

def addStudent(medium, name):
	c = cursor()
	c.execute("SELECT id FROM students WHERE medium=? AND name LIKE ?", (medium,name))
	res = c.fetchone()
	if res != None:
		return res[0]
	with conn():
		c.execute("INSERT INTO students (medium,name) VALUES (?,?)", (medium,name))
	return c.lastrowid

def getStudent(id):
	return cursor().execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()

def listStudents(trial):
	return cursor().execute("SELECT DISTINCT students.* FROM students INNER JOIN solutions ON (students.id = solutions.student) WHERE trial=?", (trial,)).fetchall()

def countStudents(trial):
	return len(listStudents(trial))

def addSolution(student, ordering, trial, timing):
	c = cursor()
	c.execute("SELECT id FROM solutions WHERE student=? AND trial=?", (student,trial))
	res = c.fetchone()
	if res != None:
		return res[0]
	with conn():
		c.execute("INSERT INTO solutions (student,ordering,trial,timing) VALUES (?,?,?,?)", (student,ordering,trial,timing))
	return c.lastrowid

def addNode(trial, name):
	c = cursor()
	c.execute("SELECT id FROM nodes WHERE trial=? AND name LIKE ?", (trial,name))
	res = c.fetchone()
	if res != None:
		return res[0]
	with conn():
		c.execute("INSERT INTO nodes (trial,name) VALUES (?,?)", (trial,name))
	return c.lastrowid

def getNode(id):
	return cursor().execute("SELECT * FROM nodes WHERE id=?", (id,)).fetchone()

def listNodes(trial):
	return cursor().execute("SELECT * FROM nodes WHERE trial=?", (trial,)).fetchall()

def countNodes(trial):
	return len(listNodes(trial))

def addAnswer(solution, ordering, src, dest, desc):
	with conn():
		cursor().execute("INSERT OR IGNORE INTO answers (solution,ordering,src,dest,description) VALUES (?,?,?,?,?)", (solution,ordering,src,dest,desc))

def addProgress(solution, ordering, action, src, dest, desc):
	actionmap = {"create": 0, "rename": 1, "remove": 2}
	action = actionmap[action]
	with conn():
		cursor().execute("INSERT OR IGNORE INTO progress (solution,ordering,action,src,dest,description) VALUES (?,?,?,?,?,?)", (solution,ordering,action,src,dest,desc))

def unverifiedAnswers(trial):
	return cursor().execute("SELECT * from answers WHERE verification = 0").fetchall()

def searchVerificationMatch(trial, src, dest, desc):
	with conn():
		return cursor().execute("SELECT * FROM answers INNER JOIN solutions ON (answers.solution = solutions.id) WHERE verification!=0 AND trial=? AND src=? AND dest=? AND description LIKE ? GROUP BY description", (trial,src,dest,desc)).fetchall()

def packVerification(args):
	flag = 0
	n = 0
	for f in VERIFICATION_FLAGS:
		if f in args:
			flag += 2**n
		n += 1
	return flag

def unpackVerification(flag):
	res = []
	for f in VERIFICATION_FLAGS:
		if flag % 2 == 1:
			res.append(f)
		flag //= 2
	return res

def listVerifications():
	return VERIFICATION_FLAGS[1:]

def setVerification(answer, flag):
	with conn():
		cursor().execute("UPDATE answers SET verification=? WHERE id=?", (flag,answer))

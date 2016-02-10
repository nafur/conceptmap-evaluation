#!/usr/bin/python3

import sys

import database
import learner
import loader
import stats

if len(sys.argv) == 1:
	print("Commands: init, import, learn, stats")
	sys.exit(0)

cmd = sys.argv[1]

if cmd == "init":
	database.init()
elif cmd == "import":
	if len(sys.argv) == 3:
		loader.loadAnswerSet(sys.argv[2])
	else:
		print("Usage: import <filename or folder>")
elif cmd == "learn":
	trial = learner.selectTrial()
	for answer in database.unverifiedAnswers(trial):
		learner.learnAnswer(trial, answer)

elif cmd == "stats":
	trial = learner.selectTrial()
	stats.generateStats(trial)

database.close()

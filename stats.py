import jinja2

import database
import plot

def printUsages(data, desc, key, str):
	data.sort(key = key)
	data = map(str, data)
	print("\n".join([desc] + list(data) + [""]))

def gatherCoreData(trial):
	return {"students": database.countStudents(trial)}

def collectNodeUsedCounts(trial, core, timing = None, verification = None):
	res = database.cursor().execute("""
SELECT
	nodes.name,
	COUNT(DISTINCT answers.solution) AS c1,
	COUNT(*) AS c3
FROM nodes
LEFT JOIN answers ON (nodes.id = answers.src OR nodes.id = answers.dest)
LEFT JOIN solutions ON (answers.solution = solutions.id)
WHERE solutions.trial=? AND (timing=? OR %d) AND (verification=? OR %d)
GROUP BY nodes.id
ORDER BY c1 desc
""" % (timing == None, verification == None), (trial,timing,verification)).fetchall()
	res = map(lambda r: [
			r[0],
			"%s (%0.2f%%)" % (r[1], r[1]*100 / core["students"]),
			"%s (%0.2f per student)" % (r[2], r[2] / core["students"])
		], res)
	return ["listing", [
		"Node",
		"Used by n students",
		"Used in n connections"
	], res]

def collectNodeUsagePlot(trial, core, timing = None, verification = None):
	res = database.cursor().execute("""
SELECT
	nodes.name,
	COUNT(DISTINCT answers.solution) AS c1
FROM nodes
LEFT JOIN answers ON (nodes.id = answers.src OR nodes.id = answers.dest)
LEFT JOIN solutions ON (answers.solution = solutions.id)
WHERE solutions.trial=? AND (timing=? OR %d) AND (verification=? OR %d)
GROUP BY nodes.id
ORDER BY c1 desc
""" % (timing == None, verification == None), (trial,timing,verification)).fetchall()
	res = list(map(lambda r: [r[0], [r[1]]], res))
	return ["image", plot.barplot("nodeusage-%s-%s.png" % (timing,verification), res)]

def collectEdgeUsedCounts(trial, core, timing = None, verification = None):
	nodes = database.listNodes(trial)
	nm = {}
	for n in nodes: nm[n["id"]] = len(nm)
	nodes = list(map(lambda n: n["name"], nodes))
	res = database.cursor().execute("""
SELECT n1.id,n2.id,answers.*
FROM nodes AS n1, nodes AS n2
INNER JOIN answers ON (n1.id = answers.src AND n2.id = answers.dest)
WHERE n1.trial = ? AND n2.trial = ?
""", (trial,trial)).fetchall()
	table = [([0] * len(nodes)) for n in nodes]
	for row in res:
		table[nm[row[0]]][nm[row[1]]] += 1
	return ["table", nodes, nodes, table]

stats = {
	"basics": {
		"nodeUsageCount": ("Node Usage Count", collectNodeUsedCounts, {}),
		"edgeCount": ("Edge Usage Count", collectEdgeUsedCounts, {}),
		"nodeUsagePlot": ("Node Usage Plot", collectNodeUsagePlot, {}),
	}
}
for t in [None, "Vorher", "Nachher"]:
	ts = "" if t == None else t
	stats["basics"].update({
		"nodeUsageCount%s" % ts: ("Node Usage Count %s" % ts, collectNodeUsedCounts, {"timing": t}),
		"nodeUsagePlot%s" % ts: ("Node Usage Plot %s" % ts, collectNodeUsagePlot, {"timing": t}),
	})
	for v in [2,4,6]:
		vs = "" if v == None else ",".join(database.unpackVerification(v))
		stats["basics"].update({
			"nodeUsageCount%s_%s" % (ts,str(v)): ("Node Usage Count %s %s" % (ts,vs), collectNodeUsedCounts, {"timing": t, "verification": v}),
			"nodeUsagePlot%s_%s" % (ts,str(v)): ("Node Usage Plot %s %s" % (ts,vs), collectNodeUsedCounts, {"timing": t, "verification": v})

		})

# Supported statistics output:
# - listing: a list of records
#	Arguments: names, records
#		names: a list of captions for the columns
#		records: a list of iterables that represent the rows
# - table: a table with arbitrary rows and columns
#	Arguments: columns, rows, cells
#		columns: a list of column labels
#		rows: a list of row labels
#		cells: a two-dimensional list that represents the cells. first dimension is row.

def generateStats(trial):
	s = {}

	print("Generating stats:")
	print("\tcore")
	core = gatherCoreData(trial)
	for group in sorted(stats):
		print("\t" + group)
		s[group] = {}
		for stat in sorted(stats[group]):
			print("\t\t" + stats[group][stat][0])
			kwargs = stats[group][stat][2]
			s[group][stat] = [stats[group][stat][0]] + stats[group][stat][1](trial, core, **kwargs)

	env = jinja2.Environment(loader=jinja2.FileSystemLoader("tpl/"))
	tpl = env.get_template("stats.tpl")
	open("out/stats_%d.html" % (trial,), "w").write(tpl.render(stats = s, core = core))

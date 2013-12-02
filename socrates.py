#!/usr/bin/python
from git import *
import peewee
from peewee import *
from datetime import datetime
#import datetime
import csv
import MySQLdb

db = MySQLDatabase('adam',user='root',passwd='root')

MAX_COUNT = 500

class namedRepo():
	def __repr__(self):
		return self.name + "/" + self.branch + " at " + self.path + " with SHA1" + self.lastSyncedSHA1
	def __str__(self):
		return self.name + "/" + self.branch + " at " + self.path + " with SHA1" + self.lastSyncedSHA1

	def __init__(self, path, name, branch, lastSyncedSHA1):
		self.path = path
		self.name = name
		self.lastSyncedSHA1 = lastSyncedSHA1
		self.branch = branch

class GitHistory2(peewee.Model):
	#hexsha = CharField(primary_key=True)
	testid = IntegerField(primary_key=True)
	hexsha = CharField(40)	
	author = CharField(100)
	authored_date = DateField()
	committer = CharField(100)
	committed_date = DateField()
	message = TextField()
	reponame = CharField(255)

	class Meta:
		database = db

def parseConfFileAtPath(path):
	reposDict = {}

	with open(path, 'r') as csvfile:
		confreader = csv.reader(csvfile, delimiter=',')
		for row in confreader:
			path = row[0]
			name = row[1]
			branch = row[2]
			lastSyncedSHA1 = ""

			if len(row) >= 4:
				#sha1 is always last item
				lastSyncedSHA1 = row[len(row)-1]

			reposDict[path] = namedRepo(path, name, branch, lastSyncedSHA1)

	return reposDict

def mergeConfAndLastSynRepos(confDict, lastSyncDict):	

	mergedDictList = []
	for k in confDict.keys():
		if k in lastSyncDict:
			mergedDictList.append(lastSyncDict[k])
		else:
			print "Missing path in last sync file: " + k
			mergedDictList.append(confDict[k])

	return mergedDictList




#create MySQL DB if it is not created yet
def createTable():
	db = MySQLdb.connect(host="localhost", 	# your host, usually localhost
	                     user="root", 		# your username
	                     passwd="root", 	# your password
	                     db="adam")			# name of the data base

	cur = db.cursor()
	
	mySQLQuery = """DROP TABLE IF EXISTS `GitHistory2`"""
	cur.execute(mySQLQuery)

	mySQLQuery = """CREATE TABLE `githistory2` (
					  `hexsha` varchar(40) NOT NULL DEFAULT '',
					  `author` varchar(255) DEFAULT NULL,
					  `authored_date` datetime DEFAULT NULL,
					  `committer` varchar(255) DEFAULT NULL,
					  `committed_date` datetime NOT NULL,
					  `message` text NOT NULL,
					  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
					  `reponame` varchar(255) NOT NULL,
					  PRIMARY KEY (`id`),
					  UNIQUE KEY `uniq_hexsha_per_repo` (`hexsha`,`reponame`),
					  FULLTEXT KEY `messageidx` (`message`)
					) ENGINE=MyISAM AUTO_INCREMENT=513005 DEFAULT CHARSET=latin1"""
				
	cur.execute(mySQLQuery)
	db.close()
	
def saveGitCommitForNameRepoToSQL(db, commit, reponame):
	authored_date = datetime.fromtimestamp(commit.authored_date)
	committed_date = datetime.fromtimestamp(commit.committed_date)
	message = commit.message
	if len(message) > 10000:
		print "commit message for " + commit.hexsha + " exceeds 10000 characters. Trimming it to 10000"
		message = message[:10000]

	query = """INSERT INTO githistory2 
				(hexsha, author, authored_date, committer, committed_date, message, reponame)
				VALUES (%s, %s, %s, %s, %s, %s, %s)"""

	db.query(query, (commit.hexsha, commit.author, authored_date, commit.committer, committed_date, message, reponame))


def populate(reposToPopulate):
	db = DB()
	for namedRepo in reposToPopulate:
		print "started " + namedRepo.name +" " + str(datetime.now())
		repo = Repo(namedRepo.path)
		assert repo.bare == False

		# traverse everything in from head to first commit.
		# Q: why not just start with head and traverse back via parents[]?
		# A: Because I don't really want to deal with merges. I hope iter_commits takes care of it for me
		i = 0	
		commitsExist = True
		while commitsExist:
			commits = repo.iter_commits(namedRepo.branch, max_count=MAX_COUNT, skip=i)
			commitsExist = False

			for commit in commits:
				commitsExist = True
				saveGitCommitForNameRepoToSQL(db, commit, namedRepo.name)
				i = i + 1
		
		print "finished:" + str(datetime.now())
	db.close()
	
class DB:
	conn = None

	def connect(self):
		self.conn = MySQLdb.connect(host="localhost", 	# your host, usually localhost
				                     user="root", 		# your username
				                     passwd="root", 	# your password
				                     db="adam")			# name of the data base

	def close(self):
		self.conn.close()

	def query(self, sql, valuesTuple):
		try:
			cursor = self.conn.cursor()
			cursor.execute(sql, valuesTuple)
		except (AttributeError, MySQLdb.OperationalError):
			print MySQLdb.OperationalError
			print valuesTuple
			self.connect()
			cursor = self.conn.cursor()
			cursor.execute(sql, valuesTuple)
		return cursor

	

#for each commit ID, walk through and add them to the DB
if __name__ == '__main__':
	createTable()
	
	confRepos = parseConfFileAtPath('socrates.conf')
	lastSyncRepos = parseConfFileAtPath('socrateslastsync.conf')

	reposToPopulate = mergeConfAndLastSynRepos(confRepos, lastSyncRepos)

	print reposToPopulate
	populate(reposToPopulate)




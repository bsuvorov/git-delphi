#!/usr/bin/python
from git import *
import peewee
from peewee import *
from datetime import datetime

db = MySQLDatabase('adam',user='root',passwd='root')

class GitHistory(peewee.Model):
	#hexsha = CharField(primary_key=True)
	testid = IntegerField(primary_key=True)
	hexsha = CharField(40)	
	author = CharField(100)
	authored_date = DateField()
	committer = CharField(100)
	committed_date = DateField()
	message = TextField()

	class Meta:
		database = db

#create MySQL DB if it is not created yet

#get list of commit ids
def populate():


	repo = Repo("/Users/bsuvorov/Development/bender/ios-v3")
	#repo = Repo("/Users/bsuvorov/Development/box/www/current_local")
	assert repo.bare == False
	
	i = 57372;
	i = i+1
	commits = repo.iter_commits('dev', max_count=900000, skip=0)
	


	#delete_query = GitHistory.delete().where(GitHistory.committed_date >= 0)
	#delete_query.execute()

	for commit in commits:
		authored_date = datetime.fromtimestamp(commit.authored_date)
		committed_date = datetime.fromtimestamp(commit.committed_date)
		tempCommit = GitHistory(testid = i,
								hexsha = commit.hexsha,
								author = commit.author,
								authored_date = authored_date,
								committer = commit.committer,
								committed_date = committed_date,
								message = commit.message)
		tempCommit.save(force_insert=True)
		i = i +1
		print i
		



#for each commit ID, walk through and add them to the DB





if __name__ == '__main__':
	populate()
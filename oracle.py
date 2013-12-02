#!/usr/bin/python
import os
import MySQLdb
import sys
import json
import cgi

DEBUG = 0

class changeDescription:
	def __init__(self, message, author, date, impact, sha1, reponame):
		self.message = message
		self.author = author
		self.date = date
		self.impact = impact
		self.sha1 = sha1
		self.reponame = reponame


def encode_changeDesc(obj):
    if isinstance(obj, changeDescription):
        return obj.__dict__
    return obj

def searchForTermWithLimit(term, limit):
	db = MySQLdb.connect(host="localhost", 	# your host, usually localhost
	                     user="root", 		# your username
	                     passwd="root", 	# your password
	                     db="adam")			# name of the data base

	# you must create a Cursor object. It will let
	#  you execute all the query you need
	cur = db.cursor() 
	# Use all the SQL you like
				
	mySQLQuery = """SELECT * FROM 
						(SELECT hexsha, author, authored_date, message, reponame, MATCH (message) AGAINST ('%s' IN NATURAL LANGUAGE MODE) as score
						FROM GITHISTORY2
						WHERE authored_date > '2012-01-01'
						ORDER BY score DESC
						LIMIT %s) a
					WHERE score > 0
					ORDER BY authored_date DESC""" % (term, limit)

	cur.execute(mySQLQuery)
	db.close()
	
	listOfChanges = []

	# print all the first cell of all the rows
	for row in cur.fetchall():
		sha1 		= row[0]
		author 		= row[1]
		# convert date to the timestamp
		timestamp	= row[2].strftime('%s')
		message 	= row[3]
		reponame	= row[4]
		impact 		= row[5]
	
		changeDesc = changeDescription(message, author, timestamp, impact, sha1, reponame)
		listOfChanges.append(changeDesc)

	return listOfChanges

if __name__ == '__main__':

	print 'Status: 200'
	print 'Content-type: application/json'
	print 'Access-Control-Allow-Origin: *\n'
	
	
	#print 'Content-type: application/json'
	#print 'Access-Control-Allow-Origin: *\n'

	# the query string, which contains the raw GET data
	# (For example, for http://example.com/myscript.py?a=b&c=d&e
	# this is "a=b&c=d&e")
	form = cgi.FieldStorage()
	if DEBUG:
		print form
	searchTerm = "test"
	if "searchterm" in form.keys():
		searchTerm = form["searchterm"].value

	if DEBUG:
		print searchTerm
	listOfChanges = searchForTermWithLimit(searchTerm, 10)

	result = "{ \"commits\": " + json.dumps(listOfChanges, default=encode_changeDesc, indent=4, separators=(',', ': ')) + "}";
	print result

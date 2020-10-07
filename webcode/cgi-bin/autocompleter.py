#!/usr/bin/env python
# Benjamin Warren, 02/2012

# get input query from url
# query database of ids, those that "match"
# return ids in json format
activate_this = '/var/www/html/py_efp/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import cgi
import MySQLdb
#import json
import efpConfig

# parameters
COLLECTION_DB = efpConfig.DB_ANNO # get the annotation database name to query
# get args for query and current dataSource
inputs = cgi.FieldStorage()
query = inputs.getvalue("term") # the search term
#dataSource = inputs.getvalue("db") # the current dataSource

# setup database connection
db = MySQLdb.connect (host = efpConfig.DB_HOST, port = efpConfig.DB_PORT, user = efpConfig.DB_USER, passwd = efpConfig.DB_PASSWD, db = COLLECTION_DB)
cur = db.cursor()

# make the query to the database
cur.execute("SELECT DISTINCT(%s)  FROM `%s` WHERE `%s` LIKE '%%%s%%'" % (efpConfig.DB_LOOKUP_GENEID_COL, efpConfig.DB_LOOKUP_TABLE, efpConfig.DB_LOOKUP_GENEID_COL, query) )
# get the query results
result = cur.fetchall()

# print output to stdout, HTML content in JSON format 
# can't figure out how to use json.dumps to convert the object into JSON format
# but I can easily do it with print staements so that will do...
print "Content-Type: text/html"
print # blank line necessary for valid html output
print "["
comma = False
for row in result:
        if (comma):
                print "," # only print the comma before row 2 onwards
        comma = True
        curr = row[0]
        print """{ "id": "%s", "label": "%s", "value": "%s" }""" % (curr, curr, curr)
print "]"
# END

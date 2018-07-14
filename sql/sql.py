import mysql.connector

# connect to mysql database for MITCourseMatch
# todo - add connection error checks here...
config = {
	'host': 'localhost',
	'user': 'root',
	'passwd': 'robertv',
	'database': 'MITCourseMatch'
}
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

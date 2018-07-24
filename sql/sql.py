import mysql.connector

# connect to mysql database for MITCourseMatch
# run: mysql -u root -p, then type password
# todo - add connection error checks here...
_config = {
	'host': 'localhost',
	'user': 'root',
	'passwd': 'robertv',
	'database': 'MITCourseMatch'
}
cnx = mysql.connector.connect(**_config)
cursor = cnx.cursor()

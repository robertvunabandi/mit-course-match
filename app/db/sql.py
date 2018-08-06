import os
import mysql.connector
import config

_config = {
	'host': os.environ.get('SQL_HOST', config.SQL_HOST),
	'user': os.environ.get("SQL_USER", config.SQL_USER),
	'passwd': os.environ.get("SQL_PASSWORD", config.SQL_PASSWORD),
	'database': os.environ.get("SQL_DATABASE", config.SQL_DATABASE)
}
try:
	cnx = mysql.connector.connect(**_config)
	cursor = cnx.cursor()
except mysql.connector.Error as err:
	print("Something went wrong: {}".format(err))

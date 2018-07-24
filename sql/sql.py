import os
import mysql.connector
import config

# todo - add connection error checks here...
_config = {
	'host': os.environ.get('SQL_HOST', config.SQL_HOST),
	'user': os.environ.get("SQL_USER", config.SQL_USER),
	'passwd': os.environ.get("SQL_PASSWORD", config.SQL_PASSWORD),
	'database': os.environ.get("SQL_DATABASE", config.SQL_DATABASE)
}
cnx = mysql.connector.connect(**_config)
cursor = cnx.cursor()

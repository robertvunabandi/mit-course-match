import config
import unittest
import mysql.connector
from typing import Callable
from app.db.sql_constants import TBL, TBLCol
import app.db.database as database


def setup():
	_cnx = mysql.connector.connect(
		host=config.SQL_HOST,
		user=config.SQL_USER,
		password=config.SQL_PASSWORD,
		database=config.SQL_TEST_DATABASE,
	)
	_cursor = _cnx.cursor()

	def sql_test_commit(method):
		def wrapper(*args, **kwargs):
			out = method(*args, **kwargs)
			_cnx.commit()
			return out

		return wrapper

	database._commit = sql_test_commit
	database.cursor = _cursor


def commit(method: Callable, db_cnx) -> Callable:
	"""
	decorator: calls cnx.commit() at the end of query in order to
	make the changes caused by the query to be permanent in the DB.
	:param method:
		method that calls an SQL query that makes changes to the data
	:param db_cnx:
		sql connection
	:return: method decorated with cnx.commit()
	"""

	def wrapper(*args, **kwargs):
		out = method(*args, **kwargs)
		db_cnx.commit()
		return out

	return wrapper


class TestDatabase(unittest.TestCase):
	# setups

	def setUp(self):
		try:
			setup()
		except mysql.connector.Error as err:
			print("Something went wrong: {}".format(err))
			self.fail(
				"Connection to DB Error: May want to check if "
				"%s DB exists" % config.SQL_TEST_DATABASE
			)

	@staticmethod
	def drop_all_tables():
		print("HEY!")
		for table in [
			TBL.Courses,
			TBL.Questions,
			TBL.AnswerChoices,
			TBL.Responses,
			TBL.ResponseMappings
		]:
			database.cursor.execute("DROP TABLE IF EXISTS %s" % table)

	def tearDown(self):
		TestDatabase.drop_all_tables()

	# tests

	def test_initialize(self):
		print("Hi")


if __name__ == '__main__':
	unittest.main()

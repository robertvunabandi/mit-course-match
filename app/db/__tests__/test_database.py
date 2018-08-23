import config
import unittest
import mysql.connector
from typing import Callable
from app.db.sql_constants import TBL, TBLCol
from app.classifier.custom_types import SQuestionType, SQuestionAnswerType
import app.db.database as database
from app.db.mit_courses import mit_courses
from app.utils.db_utils import convert_int_list_to_vector_text, quote


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
	TABLES = (
		TBL.ResponseMappings,
		TBL.Responses,
		TBL.AnswerChoices,
		TBL.Questions,
		TBL.Courses,
	)

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
		for table in TestDatabase.TABLES:
			database.cursor.execute("DROP TABLE IF EXISTS %s" % table)
			database.cnx.commit()

		tables = TestDatabase.get_tables()
		print('[TestDatabaseLog:tables-after-drop]', tables)
		assert len(tables) == 0, \
			"some tables are still in db. see print statement"

	@staticmethod
	def get_tables():
		database.cursor.execute("SHOW TABLES")
		return [row[0].lower() for row in database.cursor.fetchall()]

	def tearDown(self):
		TestDatabase.drop_all_tables()

	# tests

	def test_initialize_db(self):
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		tables = TestDatabase.get_tables()
		for table in [db_table.lower() for db_table in TestDatabase.TABLES]:
			self.assertTrue(
				table in tables,
				"table %s is missing from tables" % table
			)
		# check that courses are saved in the database
		database.cursor.execute("SELECT COUNT(*) FROM %s" % TBL.Courses)
		try:
			count = database.cursor.fetchall()[0][0]
		except IndexError:
			self.fail("fetching counts returned no rows")
		self.assertTrue(
			count == len(mit_courses),
			"mit courses length didn't match"
		)

	def test_initialize_db_twice(self):
		"""
		initialization should not throw an error if the table already exists
		because we will be making the check every time the db is ran up
		:return:
		"""
		TestDatabase.drop_all_tables()
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error the second time")

	def test_initialize_db_does_not_remove_existing_data(self):
		# drop all tables
		TestDatabase.drop_all_tables()
		# initialize
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		# store some dummy data
		query_data = (
			TBL.Questions,
			TBLCol.question,
			TBLCol.question_type,
			TBLCol.question_answer_type,
			quote(SQuestionType.type.quiz),
			quote(SQuestionAnswerType.type.multiple_choice),
		)
		database.cursor.execute(
			"INSERT INTO %s (%s, %s, %s) VALUES ('Coffee', %s, %s)" % query_data
		)
		database.cnx.commit()
		database.cursor.execute("""
			INSERT INTO %s (%s, %s, %s) VALUES (1, 'Yo', '1,4')
		""" % (TBL.AnswerChoices, TBLCol.question_id, TBLCol.choice, TBLCol.vector))
		database.cnx.commit()
		# initialize again
		database.initialize_database()
		# check that data was not removed
		database.cursor.execute("SELECT %s FROM %s" % (TBLCol.question, TBL.Questions))
		question = database.cursor.fetchall()[0][0]
		self.assertTrue(
			question == "Coffee", "question 'Coffee' was not found in db"
		)
		answer_choice_query_data = (
			TBLCol.question_id, TBLCol.choice, TBLCol.vector, TBL.AnswerChoices
		)
		database.cursor.execute("SELECT %s, %s, %s FROM %s" % answer_choice_query_data)
		row = database.cursor.fetchall()[0]
		self.assertTrue(
			row == (1, "Yo", "1,4"),
			"answer choice %s was not found in db" % str((1, "Yo", "1,4"))
		)

	def test_initialize_db_twice_doesnt_add_courses_twice(self):
		"""
		we shouldn't add courses twice. This can create unexpected
		bugs in the future.
		"""
		TestDatabase.drop_all_tables()
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		try:
			database.cursor.execute("SELECT COUNT(*) FROM %s" % TBL.Courses)
			course_count_before = database.cursor.fetchall()[0][0]
		except Exception as exception:
			print(exception)
			self.fail("wasn't able to fetch the course count")
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error the second time")
		try:
			database.cursor.execute("SELECT COUNT(*) FROM %s" % TBL.Courses)
			course_count_after = database.cursor.fetchall()[0][0]
		except Exception as exception:
			print(exception)
			self.fail("wasn't able to fetch the course count after")
		self.assertEqual(
			course_count_before,
			course_count_after,
			"courses should not be added twice!"
		)

	def test_initialize_db_later_adds_additional_courses_if_needed(self):
		"""
		If we update mit_courses.py, initialize should add the extra
		courses into the table as well.
		"""
		import app.db.mit_courses as mit_courses_
		TestDatabase.drop_all_tables()
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		try:
			database.cursor.execute("SELECT COUNT(*) FROM %s" % TBL.Courses)
			course_count_before = database.cursor.fetchall()[0][0]
		except Exception as exception:
			print(exception)
			self.fail("wasn't able to fetch the course count")
		# add 2 new courses, the initialize again
		mit_courses_.mit_courses.extend([("13", "Crash"), ("19", "Best Course")])

		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error the second time")
		try:
			database.cursor.execute("SELECT COUNT(*) FROM %s" % TBL.Courses)
			course_count_after = database.cursor.fetchall()[0][0]
		except Exception as exception:
			print(exception)
			self.fail("wasn't able to fetch the course count after")
		self.assertTrue(
			course_count_after == course_count_before + 2,
			"the additional 2 courses didn't update, \nCourses before: %d, "
			"\nCourses expected after: %d, \nCourses got after: %d" %
			(course_count_before, course_count_before + 2, course_count_after)
		)
		mit_courses_.mit_courses = mit_courses_.mit_courses[:-2]

	def test_load_courses(self):
		TestDatabase.drop_all_tables()
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		import app.db.mit_courses as mit_courses_
		course_in_db = \
			set((cn, course) for cid, cn, course in database.load_courses())
		missing_courses = [
			(cn, course)
			for cn, course in mit_courses_.mit_courses
			if (cn, course) not in course_in_db
		]
		self.assertTrue(
			len(missing_courses) == 0,
			"the courses %s are missing in the db" % repr(missing_courses),
		)

	def test_store_and_load_question(self):
		TestDatabase.drop_all_tables()
		try:
			database.initialize_database()
		except Exception as exception:
			print(exception)
			self.fail("initialization raised an error")
		question = "who are you"
		choices = \
			[("no one", "0,0,1"), ("someone", "0,1,0"), ("errone", "1,0,0")]
		database.store_question(
			question,
			SQuestionType.type.quiz,
			SQuestionAnswerType.type.multiple_choice,
			choices,
		)
		# List[Tuple[QID, SQuestion, List[Tuple[AID, SChoice, List[int]]]]
		questions = database.load_questions()
		qid_db, q_db, answers = questions[0]
		self.assertEqual(q_db, question)
		for aid, choice, vector in answers:
			s_vector = convert_int_list_to_vector_text(vector)
			self.assertTrue((choice, s_vector) in choices)


if __name__ == '__main__':
	unittest.main()

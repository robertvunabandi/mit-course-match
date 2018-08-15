from app.classifier import utils
from app.db.sql import cursor, cnx
from app.db.sql_constants import TBL, TBLCol
from typing import List, Callable, Tuple, Set, Dict
from app.classifier.custom_types import (
	SChoice,
	SQuestion,
	SCourseNumber,
	SCourse,
	QID,
	AID,
	CID,
	RID,
	MSID,
	QSID
)
from app.db.mit_courses import mit_courses
import mysql.connector.errors


def _commit(method: Callable) -> Callable:
	"""
	decorator: calls cnx._commit() at the end of query in order to
	make the changes caused by the query to be permanent in the DB.
	:param method:
		method that calls an SQL query that makes changes to the data
	:return: method decorated with cnx.commit()
	"""

	def wrapper(*args, **kwargs):
		out = method(*args, **kwargs)
		cnx.commit()
		return out

	return wrapper


@_commit
def initialize_database() -> None:
	"""
	when the database is just loaded, we need to make sure that all
	the tables are created in the db. with this method, we will not
	need to manually create tables every time we change db: it will
	just create them at initialization.
	:return: void
	"""
	# create courses table
	courses_data = (
		TBL.Courses, TBLCol.course_id, TBLCol.course_number, TBLCol.course_name
	)
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS %s (
			%s SERIAL,
			%s TINYTEXT NOT NULL,
			%s TINYTEXT NOT NULL
		);
	""" % courses_data)
	# create questions table
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS %s (
			%s SERIAL,
			%s TEXT NOT NULL
		);
	""" % (TBL.Questions, TBLCol.question_id, TBLCol.question))
	# create answer choices table
	answer_choices_query_data = (
		TBL.AnswerChoices,
		TBLCol.answer_id,
		TBLCol.question_id,
		TBLCol.choice,
		TBLCol.vector,
	)
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS %s (
			%s SERIAL,
			%s BIGINT UNSIGNED NOT NULL,
			%s TEXT NOT NULL, 
			%s TEXT NOT NULL
		);
	""" % answer_choices_query_data)
	# create response table
	responses_data = (
		TBL.Responses,
		TBLCol.response_id,
		TBLCol.course_id,
		TBLCol.course_name,
		TBLCol.time_created,
	)
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS %s (
			%s SERIAL,
			%s BIGINT UNSIGNED NOT NULL,
			-- the course name is extremely unlikely to change over
			-- a long time. so having that as a safe reference key 
			-- for the course is needed whereas course ids are 
			-- arbitrary 
			%s TINYTEXT,
			%s DATETIME(6)
		);
	""" % responses_data)
	# create response mappings table
	response_mappings_query_data = (
		TBL.ResponseMappings,
		TBLCol.response_id,
		TBLCol.question_id,
		TBLCol.answer_id,
	)
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS %s (
			%s BIGINT UNSIGNED NOT NULL,
			%s BIGINT UNSIGNED NOT NULL,
			%s BIGINT UNSIGNED NOT NULL
		);
	""" % response_mappings_query_data)
	# add ON DELETE table constraints on answer choices and response mappings
	fk_insertion_data = [
		[
			"fk_answer_choices_to_question_id",
			(TBL.AnswerChoices, TBLCol.question_id, TBL.Questions, TBLCol.question_id)
		],
		[
			"fk_response_mappings_to_response_id",
			(TBL.ResponseMappings, TBLCol.response_id, TBL.Responses, TBLCol.response_id)
		],
		[
			"fk_response_mappings_to_question_id",
			(TBL.ResponseMappings, TBLCol.question_id, TBL.Questions, TBLCol.question_id)
		],
		[
			"fk_response_mappings_to_answer_id",
			(TBL.ResponseMappings, TBLCol.answer_id, TBL.AnswerChoices, TBLCol.answer_id)
		]
	]
	for fk, fk_data in fk_insertion_data:
		query_data = (fk_data[0],) + (fk,) + fk_data[1:]
		try:
			cursor.execute("""
				ALTER TABLE %s
				ADD CONSTRAINT %s FOREIGN KEY (%s)
				REFERENCES %s (%s)
				ON DELETE CASCADE;
			""" % query_data)
		except mysql.connector.errors.IntegrityError:
			# integrity error means we ran into the duplicate key,
			# so table already had it
			pass

	# populate courses with the data we have in mit_courses.py
	course_population_data = (
		TBL.Courses,
		TBLCol.course_number,
		TBLCol.course_name,
		",".join(
			["(" + ",".join(
				[utils.quote(s) for s in course_row]
			) + ")" for course_row in mit_courses]
		),
	)
	cursor.execute("""
		INSERT INTO %s (%s, %s) VALUES %s;
	""" % course_population_data)


class _DB:
	"""
	DB provides ways to interact with the database without having to write
	db queries. This abstracts away how the database works and what queries
	are called from the caller.
	"""

	@staticmethod
	@_commit
	def store_response_set(
			responses: List[Tuple[QID, AID]],
			qsid: QSID,
			course_bundle: Tuple[CID, SCourseNumber, SCourse] or None = None) -> None:
		# first insert the whole response set
		response_salt = _DB.create_response_salt_unique()
		if course_bundle is None:
			data = (
				TBL.Responses,
				TBLCol.question_set_id,
				TBLCol.response_salt,
				str(qsid),
				response_salt
			)
			query = "INSERT INTO %s (%s, %s) VALUES (%s, %s)"
		else:
			cid, cn, course = course_bundle
			data = (
				TBL.Responses,
				TBLCol.question_set_id,
				TBLCol.response_salt,
				TBLCol.course_number,
				TBLCol.course_id,
				str(qsid),
				utils.quote(response_salt),
				utils.quote(cn),
				str(cid)
			)
			query = "INSERT INTO %s (%s, %s, %s, %s) VALUES (%s, %s, %s, %s)"
		cursor.execute(query % data)
		# then insert the questions's answers
		rid = _DB.response_id(response_salt)
		values = ", ".join([
			"(" + ", ".join([str(rid), str(qid), str(aid)]) + ")"
			for qid, aid in responses
		])
		data = (
			TBL.ResponseMappings,
			TBLCol.response_id,
			TBLCol.question_id,
			TBLCol.answer_id,
			values)
		cursor.execute("INSERT INTO %s (%s, %s, %s) VALUES %s" % data)

	@staticmethod
	@_commit
	def store_mapping_set(
			mapping_set: List[Tuple[QID, SQuestion, List[Tuple[AID, List[int]]]]],
			qsid: int,
			ms_name: str = None) -> None:
		ms_name = _DB.create_or_make_ms_name_unique(ms_name)
		# create the mapping set
		data = (
			TBL.MappingSets,
			TBLCol.question_set_id,
			TBLCol.mapping_set_name,
			str(qsid),
			ms_name
		)
		cursor.execute("INSERT INTO %s (%s, %s) VALUES (%s, '%s')" % data)
		# insert all the mappings into the db
		msid = _DB.mapping_set_id(ms_name)
		additional_values = []
		for qid, question, answer_tup in mapping_set:
			for aid, vector in answer_tup:
				additional_values.append(''.join([
					'(',
					str(msid),
					", ",
					str(qsid),
					", ",
					str(aid),
					", '",
					','.join(str(el) for el in vector),
					"')",
				]))
		data = (
			TBL.AnswerMappings,
			TBLCol.mapping_set_id,
			TBLCol.question_set_id,
			TBLCol.answer_id,
			TBLCol.vector,
			', '.join(additional_values)
		)
		print(data)
		cursor.execute("INSERT INTO %s (%s, %s, %s, %s) VALUES %s" % data)

	@staticmethod
	@_commit
	def store_question_set(
			question_set: List[Tuple[str, List[str]]],
			qs_name: str = None) -> List[Tuple[Tuple[str, str], Exception]]:
		qs_name = _DB.create_or_make_qs_name_unique(qs_name)
		# create the question set
		data = (TBL.QuestionSets, TBLCol.question_set_name, qs_name)
		cursor.execute("INSERT INTO %s (%s) VALUES ('%s')" % data)
		# add the questions into the db
		errors: List[Tuple[Tuple[str, str], Exception]] = []
		for question, choices in question_set:
			try:
				_DB.store_question(question, choices)
			except ValueError as e:
				errors.append(((question, choices), e))
		# link the questions to the question set
		qsid = _DB.question_set_id(qs_name)
		data = (
			TBL.QuestionMappings,
			TBLCol.question_set_id,
			TBLCol.question_id,
			', '.join([
				"(%d, %d)" % (qsid, _DB.question_id(question))
				for question, _ in question_set
			])
		)
		cursor.execute("INSERT INTO %s (%s, %s) VALUES %s;" % data)
		return errors

	@staticmethod
	@_commit
	def store_question(question: str, choices: List[str]) -> None:
		if _DB.question_exists_in_db(question):
			raise ValueError('this question already exists in the database')
		data = (TBL.Questions, TBLCol.question, question)
		cursor.execute("INSERT INTO %s (%s) VALUES ('%s')" % data)

		question_id = _DB.question_id(question)
		data = (
			TBL.AnswerChoices,
			TBLCol.question_id,
			TBLCol.choice,
			', '.join([
				"(" + str(question_id) + ", '" + str(choice) + "')"
				for choice in choices
			])
		)
		cursor.execute("INSERT INTO %s (%s, %s) VALUES %s;" % data)

	@staticmethod
	def question_exists_in_db(question: str) -> bool:
		return _DB.question_id(question) is not None

	@staticmethod
	def get_all_mapping_set_names() -> Set[str]:
		data = (TBLCol.mapping_set_name, TBL.MappingSets)
		cursor.execute('SELECT %s FROM %s' % data)
		return set(el[0] for el in cursor.fetchall())

	@staticmethod
	def get_all_question_set_names() -> Set[str]:
		data = (TBLCol.question_set_name, TBL.QuestionSets)
		cursor.execute('SELECT %s FROM %s' % data)
		return set(el[0] for el in cursor.fetchall())

	@staticmethod
	def get_all_response_salts() -> Set[str]:
		data = (TBLCol.response_salt, TBL.Responses)
		cursor.execute('SELECT %s FROM %s' % data)
		return set(el[0] for el in cursor.fetchall())

	@staticmethod
	def create_response_salt_unique() -> str:
		return utils.generate_unique_id(
			_DB.get_all_response_salts(),
			utils.generate_response_salt
		)

	@staticmethod
	def create_or_make_ms_name_unique(ms_name: str = None) -> str:
		return _DB.create_or_make_name_unique(
			ms_name,
			_DB.get_all_mapping_set_names(),
			utils.generate_mapping_set_name,
			utils.generate_mapping_set_extension,
			minimum_name_length=4)

	@staticmethod
	def create_or_make_qs_name_unique(qs_name: str = None) -> str:
		return _DB.create_or_make_name_unique(
			qs_name,
			_DB.get_all_question_set_names(),
			utils.generate_question_set_name,
			utils.generate_question_set_extension,
			minimum_name_length=4)

	@staticmethod
	def create_or_make_name_unique(
			name: str or None,
			taken_name_set: Set[str],
			name_generator_func: Callable,
			name_extension_generation_func: Callable,
			minimum_name_length: int = 4) -> str:
		"""
		fix the name such that it's unique when stored in the db
		:param name: a string that represents the name for a given table column
		:param taken_name_set: a set of names not to use
		:param name_generator_func: a function that generates names
		:param name_extension_generation_func:
			a functions that generate extensions for names. if this name is
			not unique, this function generates a random string. then, the
			new name will be '{name}-{generated_random_extension}'
		:param minimum_name_length: the minimum length the name has to be
		"""
		if name is None or len(name) == 0:
			return utils.generate_unique_id(
				taken_name_set, name_generator_func
			)
		name_extension = ""
		while name + name_extension in taken_name_set or len(name) < minimum_name_length:
			name_extension = '-' + name_extension_generation_func()
		return name + name_extension

	# Id and name getters

	@staticmethod
	def question_set_id(qs_name: str) -> int or None:
		return _DB.get_unique_field(
			tbl=TBL.QuestionSets,
			unique_col_name=TBLCol.question_set_id,
			target_col_name=TBLCol.question_set_name,
			target_value="'" + qs_name + "'"
		)

	@staticmethod
	def question_set_name(qsid: int) -> str or None:
		return _DB.get_unique_field(
			tbl=TBL.QuestionSets,
			unique_col_name=TBLCol.question_set_name,
			target_col_name=TBLCol.question_set_id,
			target_value=str(qsid)
		)

	@staticmethod
	def mapping_set_id(ms_name: str) -> int or None:
		return _DB.get_unique_field(
			tbl=TBL.MappingSets,
			unique_col_name=TBLCol.mapping_set_id,
			target_col_name=TBLCol.mapping_set_name,
			target_value="'" + ms_name + "'"
		)

	@staticmethod
	def mapping_set_name(msid: int) -> str or None:
		return _DB.get_unique_field(
			tbl=TBL.MappingSets,
			unique_col_name=TBLCol.mapping_set_name,
			target_col_name=TBLCol.mapping_set_id,
			target_value=str(msid)
		)

	@staticmethod
	def question_id(question: str) -> int or None:
		return _DB.get_unique_field(
			tbl=TBL.Questions,
			unique_col_name=TBLCol.question_id,
			target_col_name=TBLCol.question,
			target_value="'" + question + "'"
		)

	@staticmethod
	def response_id(response_salt: str) -> int or None:
		return _DB.get_unique_field(
			tbl=TBL.Responses,
			unique_col_name=TBLCol.response_id,
			target_col_name=TBLCol.response_salt,
			target_value="'" + response_salt + "'"
		)

	@staticmethod
	def get_unique_field(
			tbl: str,
			unique_col_name: str,
			target_col_name: str,
			target_value: str) -> int or None:
		"""
		this method expects that the column target_col_name column has unique
		values such that the id_col_name column only has one id that can match
		the given target_value. Given that, this returns that unique id.
		:param tbl: table where this is coming from
		:param unique_col_name: the column name of the id
		:param target_col_name: the target column name
		:param target_value: the target column value
		:return:
			unique_col_name from the database for the row with the unique
			target_col_name equal to the target value
		"""
		data = (unique_col_name, tbl, target_col_name, target_value)
		cursor.execute("SELECT %s FROM %s WHERE %s = %s" % data)
		row = cursor.fetchall()
		if len(row) == 0:
			return None
		return row[0][0]

	@staticmethod
	def answer_choices_for_question(question: str) -> List[Tuple[int, str]]:
		question_id = _DB.question_id(question)
		if question_id is None:
			raise ValueError('the question given does not exists')
		return _DB.answer_choices_for_question_id(question_id)

	@staticmethod
	def answer_choices_for_question_id(
			question_id: int) -> List[Tuple[int, str]]:
		data = (
			TBLCol.answer_id,
			TBLCol.choice,
			TBL.AnswerChoices,
			TBLCol.question_id,
			question_id
		)
		cursor.execute("SELECT %s, %s FROM %s WHERE %s = '%s'" % data)
		return [(aid, choice) for aid, choice in cursor.fetchall()]

	@staticmethod
	def load_question_set(
			qsid: int
	) -> List[Tuple[QID, SQuestion, List[Tuple[AID, SChoice]]]]:
		data = (
			TBLCol.question_id,
			TBL.QuestionMappings,
			TBLCol.question_set_id,
			qsid,
		)
		assert _DB.question_set_name(qsid) is not None, \
			"there doesn't exist a question set with " \
			"this qsid -> %s" % str(qsid)
		cursor.execute("SELECT %s FROM %s WHERE %s = %s" % data)
		question_id_list = [row[0] for row in cursor.fetchall()]
		question_set_result = []
		for qid in question_id_list:
			data = (
				TBLCol.answer_id, TBLCol.choice, TBLCol.question,
				TBL.AnswerChoices, TBL.Questions,
				TBLCol.question_id, TBLCol.question_id,
				TBLCol.question_id, qid
			)
			cursor.execute("""
				SELECT a.%s, a.%s, b.%s 
				FROM %s a LEFT JOIN %s b 
				ON a.%s = b.%s 
				WHERE a.%s = %s
				""" % data)
			rows = cursor.fetchall()
			question = SQuestion(rows[0][2])
			question_set_result.append(
				(
					QID(qid),
					question,
					[(AID(aid), SChoice(choice)) for aid, choice, _ in rows],
				)
			)
		return question_set_result

	@staticmethod
	def load_mapping_set(msid: MSID) -> List[Tuple[QID, AID, str]]:
		data = (
			TBLCol.question_id, TBLCol.answer_id, TBLCol.vector,
			TBL.AnswerMappings, TBL.AnswerChoices,
			TBLCol.answer_id, TBLCol.answer_id,
			TBLCol.mapping_set_id, str(msid)
		)
		cursor.execute("""
			SELECT b.%s, a.%s, a.%s 
			FROM %s a JOIN %s b 
			ON a.%s = b.%s 
			WHERE a.%s = %s
			""" % data)
		return cursor.fetchall()

	@staticmethod
	def load_question_set_responses(qsid: QSID) -> Dict[Tuple[RID, CID], Dict[QID, AID]]:
		data = (
			TBLCol.response_id, TBLCol.course_id,
			TBLCol.question_id, TBLCol.answer_id,
			TBL.ResponseMappings,
			TBLCol.response_id, TBLCol.course_id, TBL.Responses,
			TBLCol.question_set_id, str(qsid), TBLCol.course_id,
			TBLCol.response_id, TBLCol.response_id,
		)
		cursor.execute("""
			SELECT a.%s, b.%s, a.%s, a.%s FROM 
			%s a JOIN (
				SELECT %s, %s FROM %s 
				WHERE %s = %s AND %s IS NOT NULL
			) b ON a.%s = b.%s
		""" % data)
		data = {}
		for rid, cid, qid, aid in cursor.fetchall():
			key = (RID(rid), CID(cid))
			data[key] = data.get(key, {})
			data[key][QID(qid)] = AID(aid)
		return data

	@staticmethod
	def load_response(rid: RID) -> Dict[QID, AID] or None:
		data = (
			TBLCol.question_id,
			TBLCol.answer_id,
			TBL.ResponseMappings,
			TBLCol.response_id,
			str(rid)
		)
		cursor.execute("SELECT %s, %s FROM %s WHERE %s = %s" % data)
		rows = cursor.fetchall()
		if len(rows) == 0:
			return None
		data = {}
		for qid, aid in rows:
			data[QID(qid)] = AID(aid)
		return data

	@staticmethod
	def load_courses():
		data = (
			TBLCol.course_number,
			TBLCol.course_name,
			TBLCol.course_id,
			TBL.Courses
		)
		cursor.execute("SELECT %s, %s, %s FROM %s" % data)
		return cursor.fetchall()


# Exposing functions that will be used publicly
store_question_set = _DB.store_question_set
load_question_set = _DB.load_question_set
load_mapping_set = _DB.load_mapping_set
store_mapping_set = _DB.store_mapping_set
load_courses = _DB.load_courses
store_response_set = _DB.store_response_set
load_question_set_responses = _DB.load_question_set_responses
load_response = _DB.load_response

# initialize the database
# initialize_database()

if __name__ == '__main__':
	# cursor.execute('SELECT * FROM Questions WHERE question = \'coffee?\';')
	# print(cursor.fetchall())
	# DB.store_question('Ice Cream?', ['nah', 'YEAH', 'hell no'])
	# cursor.execute('SELECT aid, qid, choice FROM AnswerChoices;')
	# print(cursor.fetchall())
	# print(_DB.answer_choices_for_question('coffee?'))
	# print(_DB.load_mapping_set(MSID(2)))
	cursor.execute("SELECT * FROM QuestionSets")
	rows = cursor.fetchall()
	print(rows)

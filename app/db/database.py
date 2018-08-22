from app.utils import generator_util
from app.utils.db_utils import (
	convert_to_query_values,
	convert_vector_text_to_int_list,
	quote,
)
from app.db.sql import cursor, cnx
from app.db.sql_constants import TBL, TBLCol
from typing import List, Callable, Tuple, Dict, Union
from app.classifier.custom_types import (
	SChoice,
	SVector,
	SQuestion,
	SCourseNumber,
	SCourse,
	QID,
	AID,
	CID,
	RID,
)
import app.db.db_initializer as db_initializer


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
	""" see db_initializer.py """
	db_initializer.initialize_database(cursor)


class _DB:
	"""
	DB provides ways to interact with the database without having to
	write db queries. This abstracts away how the database works and
	what queries are called from the caller.
	"""

	# questions

	@staticmethod
	@_commit
	def store_question(
		question: str,
		choices: List[Tuple[str, str]]
	) -> Tuple[QID, SQuestion, List[Tuple[SChoice, SVector]]]:
		if _DB.question_exists_in_db(question):
			raise ValueError("this question already exists in the database")
		data = (TBL.Questions, TBLCol.question, question)
		cursor.execute("INSERT INTO %s (%s) VALUES ('%s')" % data)
		question_id = _DB.question_id(question)
		data = (
			TBL.AnswerChoices,
			TBLCol.question_id,
			TBLCol.choice,
			TBLCol.vector,
			', '.join([
				"(" + ",".join([
					str(question_id),
					quote(str(choice)),
					quote(str(vector))
				]) + ")"
				for choice, vector in choices
			]),
		)
		cursor.execute("INSERT INTO %s (%s, %s, %s) VALUES %s;" % data)
		answers = \
			[(SChoice(choice), SVector(vector)) for choice, vector in choices]
		return QID(question_id), SQuestion(question), answers

	@staticmethod
	def question_exists_in_db(question: str) -> bool:
		return _DB.question_id(question) is not None

	@staticmethod
	def load_questions(
	) -> List[Tuple[QID, SQuestion, List[Tuple[AID, SChoice, List[int]]]]]:
		data = (
			TBLCol.question_id,
			TBLCol.question,
			TBLCol.answer_id,
			TBLCol.choice,
			TBLCol.vector,
			TBL.Questions,
			TBL.AnswerChoices,
			TBLCol.question_id,
			TBLCol.question_id,
		)
		cursor.execute("""
			SELECT a.%s, a.%s, b.%s, b.%s, b.%s 
			FROM %s a JOIN %s b ON a.%s = b.%s
		""" % data)
		result = {}
		for qid, question, aid, choice, vector in cursor.fetchall():
			question_list = result.get((qid, question), [])
			question_list.append(
				(aid, choice, convert_vector_text_to_int_list(vector))
			)
			result[(qid, question)] = question_list
		return [
			(qid, question, result[(qid, question)])
			for (qid, question) in result
		]

	# courses

	@staticmethod
	def load_courses() -> List[Tuple[CID, SCourseNumber, SCourse]]:
		data = (
			TBLCol.course_id,
			TBLCol.course_number,
			TBLCol.course_name,
			TBL.Courses,
		)
		cursor.execute("SELECT %s, %s, %s FROM %s" % data)
		return cursor.fetchall()

	# responses

	@staticmethod
	def load_labelled_responses() -> Dict[Tuple[RID, SCourseNumber], Dict[QID, AID]]:
		data = (
			TBLCol.response_id,
			TBLCol.course_number,
			TBLCol.question_id,
			TBLCol.answer_id,
			TBL.Responses,
			TBL.ResponseMappings,
			TBLCol.response_id,
			TBLCol.response_id,
			TBLCol.course_number,
		)
		cursor.execute("""
			SELECT a.%s, b.%s, b.%s, b.%s 
			FROM %s a 
				JOIN %s b ON a.%s = b.%s
			WHERE
				a.%s IS NOT NULL
		""" % data)
		result = {}
		for rid_, cn_, qid_, aid_ in cursor.fetchall():
			rid, cn, qid, aid = \
				RID(rid_), SCourseNumber(cn_), QID(qid_), AID(aid_)
			dic = result.get((rid, cn), {})
			dic[qid] = aid
			result[(rid, cn)] = dic
		return result

	@staticmethod
	def load_response(rid: RID) -> Dict[QID, AID] or None:
		data = (
			TBLCol.question_id,
			TBLCol.answer_id,
			TBL.ResponseMappings,
			TBLCol.response_id,
			str(rid),
		)
		cursor.execute("SELECT %s, %s FROM %s WHERE %s = %s" % data)
		rows = cursor.fetchall()
		if len(rows) == 0:
			return None
		return {QID(qid): AID(aid) for qid, aid in rows}

	@staticmethod
	@_commit
	def store_response(
		response: Dict[QID, AID],
		cn: SCourseNumber = None,
	) -> RID:
		salt = _DB.create_unique_response_salt()
		data = (
			TBL.Responses,
			TBLCol.course_number,
			TBLCol.response_salt,
			"NULL" if cn is None else cn,
			salt,
		)
		cursor.execute("INSERT INTO %s (%s, %s) VALUES (%s, %s)" % data)
		rid = RID(_DB.response_id(salt))
		values = [(rid, qid, response[qid]) for qid in response]
		data = (
			TBL.ResponseMappings,
			TBLCol.response_id,
			TBLCol.question_id,
			TBLCol.answer_id,
			convert_to_query_values(values),
		)
		cursor.execute("INSERT INTO %s (%s, %s, %s) VALUES %s;" % data)
		return rid

	@staticmethod
	def create_unique_response_salt() -> str:
		cursor.execute(
			"SELECT %s FROM %s" %
			(TBLCol.response_salt, TBL.Responses)
		)
		return generator_util.generate_unique_id(
			set(el[0] for el in cursor.fetchall()),
			generator_util.generate_response_salt,
		)

	# id and name getters

	@staticmethod
	def question_id(question: str) -> Union[QID, int, None]:
		return _DB.get_unique_field(
			tbl=TBL.Questions,
			unique_col_name=TBLCol.question_id,
			target_col_name=TBLCol.question,
			target_value=quote(question),
		)

	@staticmethod
	def response_id(response_salt: str) -> Union[RID, int, None]:
		return _DB.get_unique_field(
			tbl=TBL.Responses,
			unique_col_name=TBLCol.response_id,
			target_col_name=TBLCol.response_salt,
			target_value=quote(response_salt),
		)

	@staticmethod
	def get_unique_field(
		tbl: str,
		unique_col_name: str,
		target_col_name: str,
		target_value: str,
	) -> str or int or None:
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
		cursor.execute(
			"SELECT %s FROM %s WHERE %s = %s" %
			(unique_col_name, tbl, target_col_name, target_value)
		)
		row = cursor.fetchall()
		if len(row) == 0:
			return None
		return row[0][0]


# Exposing functions that will be used publicly
load_courses = _DB.load_courses
load_questions = _DB.load_questions
load_response = _DB.load_response
load_labelled_responses = _DB.load_labelled_responses
store_question = _DB.store_question
store_response = _DB.store_response

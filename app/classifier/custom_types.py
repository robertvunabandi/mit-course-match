import numpy as np
from typing import Any
from app.db.sql_constants import QuestionTypes, QuestionAnswerTypes


class Vector(np.ndarray):
	@staticmethod
	def assert_is_np_array(
		vec: np.ndarray,
		err_msg: str = "this is not a numpy array") -> None:
		assert isinstance(vec, np.ndarray), err_msg

	@staticmethod
	def is_col_vector(vec: Any) -> bool:
		Vector.assert_is_np_array(vec)
		return vec.shape[1] == 1

	@staticmethod
	def is_row_vector(vec: Any) -> bool:
		Vector.assert_is_np_array(vec)
		return vec.shape[0] == 1

	@staticmethod
	def one_hot(element_count: int):
		""" one hot representation in row vectors for all elements """
		vectors, base_vector = [], np.zeros((element_count, 1))
		for i in range(element_count):
			vector = base_vector.copy()
			vector[i] = 1
			vectors.append(vector)
		return vectors

	@staticmethod
	def one_hot_repr(element_count: int, index: int) -> np.ndarray:
		""" one hot representation in a row vector """
		vector = np.zeros((1, element_count))
		vector[0, index] = 1
		return vector

	def __instancecheck__(self, instance):
		return isinstance(instance, np.ndarray)


class IntVectorList:
	element_types = {int}

	def __instancecheck__(self, instance: Any) -> bool:
		if type(instance) != list:
			return False
		for item in instance:
			if type(item) not in IntVectorList.element_types:
				return False
		return True


class FloatVectorList:
	element_types = {int, float}


class SpecialString(str):
	"""
	This string ensures that any class that inherit from this and edits
	the __str__ method (i.e. prepends values to it) will have the property
	that when passed onto another class that inherits from this only takes
	the original string. For example, below QuestionID prepends "QuestionID:"
	before the string and AnswerSetID prepends "AnswerSetID:" before the
	string. However, calling AnswerSetID(QuestionID("hello")) will result
	only in "AnswerSetID:hello" when invoking the string method.

	However, DO NOT MODIFY __repr__ OF SUBCLASSES.
	"""

	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls, str(args[0]))
		return obj

	def __repr__(self):
		return super(SpecialString, self).__repr__()[1:-1]

	def tostring(self):
		return str(self)


"""
The following classes are just strings. We add the "S" prefix to indicate that
they are just strings.
"""


class SQSName(SpecialString):
	def __repr__(self):
		return "QuestionSetName:" + super(SQSName, self).__repr__()


class SMSName(SpecialString):
	def __repr__(self):
		return "MappingSetName:" + super(SMSName, self).__repr__()


class SQuestion(SpecialString):
	def __repr__(self):
		return "Question:" + super(SQuestion, self).__repr__()


class SQuestionType(SpecialString):
	def __repr__(self):
		return "QuestionType:" + super(SQuestionType, self).__repr__()

	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls, str(args[0]))
		SQuestionType.assert_is_valid_question_type(obj)
		return obj

	@staticmethod
	def is_question_type(s: Any) -> bool:
		return QuestionTypes.is_valid(s)

	@staticmethod
	def assert_is_valid_question_type(s: Any) -> None:
		assert QuestionTypes.is_valid(s), \
			"argument (%s) must be a question type" % str(s)


class SQuestionAnswerType(SpecialString):
	def __repr__(self):
		return "QuestionAnswerType:" + super(SQuestionAnswerType, self).__repr__()

	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls, str(args[0]))
		SQuestionAnswerType.assert_is_valid_question_answer_type(obj)
		return obj

	@staticmethod
	def is_question_answer_type(s: Any) -> bool:
		return QuestionAnswerTypes.is_valid(s)

	@staticmethod
	def assert_is_valid_question_answer_type(s: Any) -> None:
		assert QuestionAnswerTypes.is_valid(s), \
			"argument (%s) must be a question answer type" % str(s)


class SCourse(SpecialString):
	def __repr__(self):
		return "Course:" + super(SCourse, self).__repr__()


class SChoice(SpecialString):
	def __repr__(self):
		return "AnswerChoice:" + super(SChoice, self).__repr__()


class SVector(SpecialString):
	def __repr__(self):
		return "ChoiceVector:" + super(SVector, self).__repr__()


class SCourseNumber(SpecialString):
	def __repr__(self):
		return "CourseNumber:" + super(SCourseNumber, self).__repr__()


"""
The following classes are IDs. Their string representation is different.
"""


class SpecialInt(int):
	""" see SpecialString: this has the same property. """

	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls, int(args[0]))
		return obj


class IntID(SpecialInt):
	def __repr__(self):
		return "ID:" + super(IntID, self).__repr__()


class QID(IntID):
	def __repr__(self):
		return "Q" + super(QID, self).__repr__()


class AID(IntID):
	def __repr__(self):
		return "A" + super(AID, self).__repr__()


class QSID(IntID):
	def __repr__(self):
		return "QS" + super(QSID, self).__repr__()


class RID(IntID):
	def __repr__(self):
		return "R" + super(RID, self).__repr__()


class CID(IntID):
	def __repr__(self):
		return "C" + super(CID, self).__repr__()


class MSID(IntID):
	def __repr__(self):
		return "MS" + super(MSID, self).__repr__()

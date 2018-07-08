import numpy as np
from typing import Any


class Vector(np.ndarray):
	@staticmethod
	def assert_is_np_array(
			vec: np.ndarray,
			err_msg: str = 'this is not a numpy array') -> None:
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


class ColumnVector(Vector):
	def __instancecheck__(self, instance: Any) -> bool:
		return Vector.is_col_vector(instance)


class RowVector(Vector):
	def __instancecheck__(self, instance: Any) -> bool:
		return Vector.is_row_vector(instance)


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


class MITCourse:
	# NOTE - this is not used yet anywhere, so it can be safely deleted
	def __init__(self, course_number: str, course_name: str) -> None:
		self.number = course_number
		self.name = course_name

	def __str__(self) -> str:
		return self.name

	def __repr__(self) -> str:
		return 'MITCourse::' + self.__str__()

	def __hash__(self) -> int:
		return hash(str(self.name))

	def __lt__(self, other) -> bool:
		return self.name < other.name

	def __eq__(self, other) -> bool:
		return self.name == other.name and self.number == other.number

	def __le__(self, other) -> bool:
		return self.__lt__(other) or self.__eq__(other)

	def string(self) -> str:
		return '%s, %s' % (self.number, self.name)


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


class SpecialInt(int):
	""" see SpecialString: this has the same property. """

	def __new__(cls, *args, **kwargs):
		obj = super().__new__(cls, int(args[0]))
		return obj


"""
The following classes are just strings. We add the "S" prefix to indicate that
they are just strings.
"""


class SQSName(SpecialString):
	pass


class SMSName(SpecialString):
	pass


class SQuestion(SpecialString):
	pass


class SCourse(SpecialString):
	pass


class SChoice(SpecialString):
	pass


class SCourseNumber(SpecialString):
	pass


class SAnswer(SpecialString):
	pass


"""
The following classes are IDs. Their string representation is different.
"""


class IntID(SpecialInt):
	def __repr__(self):
		return 'ID::' + super(IntID, self).__repr__()


class QID(IntID):
	def __repr__(self):
		return 'Q' + super(QID, self).__repr__()


class AID(IntID):
	def __repr__(self):
		return 'A' + super(AID, self).__repr__()


class QSID(IntID):
	def __repr__(self):
		return 'QS' + super(QSID, self).__repr__()


class RID(IntID):
	def __repr__(self):
		return 'R' + super(RID, self).__repr__()


class CID(IntID):
	def __repr__(self):
		return 'C' + super(CID, self).__repr__()


class MSID(IntID):
	def __repr__(self):
		return 'MS' + super(MSID, self).__repr__()


class StringID(SpecialString):
	def __repr__(self):
		return 'ID::' + super(StringID, self).__repr__()


class QuestionID(StringID):

	def __repr__(self):
		return 'Question' + super(QuestionID, self).__repr__()


class QuestionSetID(StringID):
	def __repr__(self):
		return 'QuestionSet' + super(QuestionSetID, self).__repr__()


class MappingSetID(StringID):
	def __repr__(self):
		return 'MappingSet' + super(MappingSetID, self).__repr__()


class AnswerSetID(StringID):
	def __repr__(self):
		return 'AnswerSet' + super(AnswerSetID, self).__repr__()


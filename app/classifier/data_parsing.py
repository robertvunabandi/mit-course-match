from app.utils import number_utils
import numpy as np
from typing import Iterable, Tuple, List, Dict, Set
from app.db import database
from app.utils.deprecate_util import deprecated
from app.classifier.custom_types import (
	Vector,
	SCourseNumber,
	SCourse,
	QID,
	AID,
	CID,
	RID,
	QSID,
	MSID,
	SQuestion,
	SChoice,
)


# ------------------------------------------------------------
# ------------------------------------------------------------
@deprecated(reason="moved to new model. see data_manager.py")
class CourseObj:
	def __init__(self) -> None:
		self.cid_to_course: Dict[CID, Tuple[SCourseNumber, SCourse]] = None
		self.cid_to_index: Dict[CID, int] = None
		self.cid_resolver: Dict[CID or SCourse or SCourseNumber, CID] = None
		self.cid_to_vector: Dict[CID, np.ndarray] = {}
		self.course_count: int = None
		self.setup()

	def setup(self) -> None:
		cid_to_course, cid_resolver, cids = {}, {}, []
		for cn, course_name, cid in database.load_courses():
			cid_to_course[CID(cid)] = (SCourseNumber(cn), SCourse(course_name))
			cid_resolver[CID(cid)] = CID(cid)
			cid_resolver[SCourse(course_name)] = CID(cid)
			cid_resolver[SCourseNumber(cn)] = cid
			cids.append(cid)
		self.cid_to_course, self.cid_resolver = cid_to_course, cid_resolver
		cid_to_index = {}
		for index, cid in enumerate(sorted(cids)):
			cid_to_index[cid] = index
		self.cid_to_index = cid_to_index
		self.course_count = len(cids)

	def get_course_vector(
		self,
		course_identifier: CID or SCourse or SCourseNumber) -> np.ndarray:
		cid = self.cid_resolver[course_identifier]
		if cid in self.cid_to_vector:
			return self.cid_to_vector[cid]
		course_index = self.cid_to_index[cid]
		self.cid_to_vector[cid] = Vector.one_hot_repr(self.course_count, course_index)
		return self.get_course_vector(cid)

	def get_course_bundle(
		self,
		cid_identifier: CID or SCourse or SCourseNumber) -> Tuple[CID, SCourseNumber, SCourse]:
		cid = self.cid_resolver[cid_identifier]
		cn, course = self.cid_to_course[cid]
		return cid, cn, course

	def get_course_index(
		self,
		cid_identifier: CID or SCourse or SCourseNumber) -> int:
		return self.cid_to_index[self.cid_resolver[cid_identifier]]

	def cid(self, cid_identifier: CID or SCourse or SCourseNumber) -> CID:
		return self.cid_resolver[cid_identifier]

	def course_ids(self) -> CID:
		for cid in self.cid_to_course:
			yield cid


@deprecated(reason="moved to new model. see data_manager.py")
class QuestionAnswerManager:
	def __init__(self, qsid: QSID, msid: MSID) -> None:
		self.qsid, self.msid = qsid, msid
		self.qid_resolver: Dict[QID or SQuestion, QID] = None
		self.aid_resolver: Dict[QID, Dict[AID or SChoice, AID]] = None
		self.question_order: Dict[QID, int] = None
		self.question_index_in_answer_vector: Dict[QID, int] = None
		self.answer_order: Dict[QID, Dict[AID, int]] = None
		self.aid_to_qid_map: Dict[AID, QID] = None
		self.answer_to_vector_map: Dict[QID, Dict[AID, np.ndarray]] = None
		self.question_dimension_map: Dict[QID, int] = None
		self._input_dimension: int = None
		self._qids: Set[QID] = None
		self._aids: Set[Tuple[QID, AID]] = None
		self.setup()

	def setup(self) -> None:
		# load variables using the question set is
		question_resolver, answer_resolver = {}, {}
		question_list, answer_map_list = [], {}
		question_order, answer_order = {}, {}
		aid_to_qid_map = {}
		qids = set()
		for qid_, question_, answers in database.load_question_set(self.qsid):
			qid, question = QID(qid_), SQuestion(question_)
			question_resolver[question] = qid
			question_resolver[qid] = qid
			answer_resolver[qid] = {}
			answer_map_list[qid], answer_order[qid] = [], {}
			for aid, choice in answers:
				answer_resolver[qid][choice] = aid
				answer_resolver[qid][aid] = aid
				answer_map_list[qid].append(choice)
				aid_to_qid_map[aid] = qid
			for index, aid in enumerate(sorted(answer_map_list[qid])):
				answer_order[qid][aid] = index
			question_list.append(qid)
			qids.add(qid)
		for index, qid in enumerate(sorted(question_list)):
			question_order[qid] = index

		self.qid_resolver = question_resolver
		self.aid_resolver = answer_resolver
		self.question_order = question_order
		self.answer_order = answer_order
		self.aid_to_qid_map = aid_to_qid_map
		self._qids = qids

		# load variables from the mapping set id
		answer_to_vector_map = {}
		question_dimension_map = {}
		input_dimension_contributions = {}
		aids = set()
		for qid, aid, vector_text in database.load_mapping_set(self.msid):
			vector = np.array([[int(el) for el in vector_text.split(',')]])
			question_dimension_map[qid] = question_dimension_map.get(qid, None)
			answer_to_vector_map[qid] = answer_to_vector_map.get(qid, {})
			answer_to_vector_map[qid][aid] = vector
			if question_dimension_map[qid] is None:
				question_dimension_map[qid] = vector.shape[1]
			assert question_dimension_map[qid] == vector.shape[1], \
				"dimensions for the same qid don't match -> %s" % str(qid)
			input_dimension_contributions[qid] = question_dimension_map[qid]
			aids.add((qid, aid))

		# find the index of each question in the vector
		# this is going to be a bit obscure
		question_index_in_answer_vector = {}
		ordered_qids_by_index = sorted(
			[(qid, question_order[qid]) for qid in question_order],
			key=lambda tup: tup[1]
		)
		for qid, index in ordered_qids_by_index:
			if index == 0:
				continue
			prev_qid = ordered_qids_by_index[index - 1][0]
			prev_qid_dim = input_dimension_contributions[prev_qid]
			# this will only apply to the very first element, which
			# automatically will then get the index 0 as needed
			question_index_in_answer_vector[prev_qid] = \
				question_index_in_answer_vector.get(prev_qid, 0)
			question_index_in_answer_vector[qid] = \
				question_index_in_answer_vector[prev_qid] + prev_qid_dim

		self.answer_to_vector_map = answer_to_vector_map
		self.question_dimension_map = question_dimension_map
		self.question_index_in_answer_vector = question_index_in_answer_vector
		self._input_dimension = sum(input_dimension_contributions.values())
		self._aids = aids

	def question_index(self, q_identifier: QID or SQuestion) -> int:
		return self.question_index_in_answer_vector[
			self.qid_resolver[q_identifier]
		]

	def question_dimension(self, q_identifier: QID or SQuestion) -> int:
		return self.question_dimension_map[self.qid_resolver[q_identifier]]

	def answer_vector(
		self,
		q_identifier: QID or SQuestion,
		aid_identifier: AID or SChoice) -> np.ndarray:
		qid = self.qid_resolver[q_identifier]
		aid = self.aid_resolver[qid][aid_identifier]
		return self.answer_to_vector_map[qid][aid]

	def answer_vector_from_aid(self, aid: AID) -> np.ndarray:
		return self.answer_to_vector_map[self.aid_to_qid_map[aid]][aid]

	def get_qid(self, qid_indentifier: QID or SQuestion) -> QID:
		return self.qid_resolver[qid_indentifier]

	def get_aid(
		self,
		qid_identifier: QID or SQuestion,
		aid_identifier: AID or SChoice) -> AID:
		return self.aid_resolver[self.get_qid(qid_identifier)][aid_identifier]

	def question_ids(self) -> Iterable[QID]:
		for qid in self._qids:
			yield qid

	def answer_ids(self) -> Iterable[Tuple[QID, AID]]:
		for aid in self._aids:
			yield aid

	@property
	def input_dimension(self) -> int:
		return self._input_dimension


@deprecated(reason="moved to new model. see data_manager.py")
class DataManager:
	def __init__(self, qsid: QSID, msid: MSID) -> None:
		number_utils.assert_valid_db_id(qsid, QSID.__name__)
		number_utils.assert_valid_db_id(msid, MSID.__name__)
		self.qsid, self.msid = qsid, msid
		self.course_obj: CourseObj = None
		self.qa_manager: QuestionAnswerManager = None
		self.base_answer_vector: np.ndarray = None
		self.answer_vector: np.ndarray = None
		self.raw_responses: Dict[QID, AID] = None
		self.setup()

	def setup(self) -> None:
		self.course_obj = CourseObj()
		self.qa_manager = QuestionAnswerManager(self.qsid, self.msid)
		self.base_answer_vector = np.zeros((1, self.input_dimension))
		self.raw_responses = {qid: None for qid in self.qa_manager.question_ids()}
		self.refresh_responses()

	@property
	def input_dimension(self) -> int:
		return self.qa_manager.input_dimension

	@property
	def output_dimension(self) -> int:
		return self.course_obj.course_count

	def set_answer(
		self,
		qid_identifier: SQuestion or QID,
		aid_identifier: SChoice or AID) -> None:
		index = self.qa_manager.question_index(qid_identifier)
		vector = self.qa_manager.answer_vector(qid_identifier, aid_identifier)
		self.answer_vector[:, index:index + vector.shape[1]] = vector
		qid = self.qa_manager.get_qid(qid_identifier)
		aid = self.qa_manager.get_aid(qid, aid_identifier)
		self.raw_responses[qid] = aid

	def refresh_responses(self) -> None:
		self.answer_vector = self.base_answer_vector.copy()

	def load_training_data(self) -> Tuple[np.ndarray, np.ndarray] or Tuple[None, None]:
		"""
		load the training data that matches self's qsid. this is data stored
		in the db. this data are the labelled responses in the database. the
		data is directly converted to vectors to be used in the _classifier.
		the conversion is done through using the mapping from self's msid.
		:return: a tuple of data and label for that data
		"""
		responses: Dict[Tuple[RID, CID], Dict[QID, AID]] = \
			database.load_question_set_responses(self.qsid)
		data: List[np.ndarray] = []
		labels: List[np.ndarray] = []
		for (rid, cid) in responses:
			data.append(self.vector_from_responses(responses[(rid, cid)]))
			labels.append(self.course_obj.get_course_vector(cid))
		if len(data) == 0:
			return None, None
		return np.vstack(data), np.vstack(labels)

	def vector_from_responses(
		self,
		response: Dict[QID or SQuestion, AID or SChoice]) -> np.ndarray:
		self.refresh_responses()
		for qid_identifier in response:
			self.set_answer(qid_identifier, response[qid_identifier])
		vector = self.answer_vector.copy()
		self.refresh_responses()
		return vector

	def store_responses(
		self,
		cid_identifier: SCourse or CID or SCourseNumber = None) -> None:
		course_bundle = None
		if cid_identifier is not None:
			course_bundle = self.course_obj.get_course_bundle(cid_identifier)
		self.assert_all_questions_answered()
		responses: List[Tuple[QID, AID]] = [
			(qid, self.raw_responses[qid]) for qid in self.raw_responses
		]
		database.store_response_set(responses, self.qsid, course_bundle)

	def assert_all_questions_answered(self):
		for qid in self.raw_responses:
			assert self.raw_responses.get(qid, None) is not None, \
				'the answer with qid %s is not answered' % str(qid)

	def question_ids(self) -> Iterable[QID]:
		yield from self.qa_manager.question_ids()

	def answer_ids(self) -> Iterable[AID]:
		yield from self.qa_manager.answer_ids()

	def course_ids(self) -> Iterable[CID]:
		yield from self.course_obj.course_ids()

from typing import Iterable, Dict, Set, List
from app.classifier.custom_types import SQuestion, SChoice, QID, AID
import numpy as np
import app.db.database as database
from app.utils.resolver_util import ValueResolver


class QuestionAnswerManager:
	def __init__(self) -> None:
		self.qid_resolver: ValueResolver[QID or SQuestion, QID] = None
		self.aid_resolver: Dict[QID, ValueResolver[AID or SChoice, AID]] = None
		self.question_dimension_map: Dict[QID, int] = None
		self.aid_vector_map: Dict[QID, Dict[AID, List[int]]] = None
		self.input_dimension: int = None
		self.qid_set: Set[QID] = None
		self.setup()

	def setup(self) -> None:
		qid_resolver, aid_resolver = ValueResolver(), {}
		question_dimension_map = {}
		aid_vector_map = {}
		qid_set = set()
		for qid, question, answer_list in database.load_questions():
			qid_resolver[[qid, question]] = qid
			question_dimension = None
			# answer_list should never be larger than 10 and usually max 4
			for aid, choice, vector in answer_list:
				aid_resolver_for_qid = aid_resolver.get(qid, ValueResolver())
				aid_resolver_for_qid[[aid, choice]] = aid
				aid_resolver[qid] = aid_resolver_for_qid
				if question_dimension is None:
					question_dimension = len(vector)
				assert question_dimension == len(vector), \
					"dimension must be the same across all answer choices. " \
					"%s fails this check" % repr(qid)
				dic = aid_vector_map.get(qid, {})
				dic[aid] = vector
				aid_vector_map[qid] = dic
			question_dimension_map[qid] = question_dimension
			qid_set.add(qid)
		self.qid_resolver, self.aid_resolver = qid_resolver, aid_resolver
		self.question_dimension_map = question_dimension_map
		self.aid_vector_map = aid_vector_map
		self.input_dimension = \
			sum([question_dimension_map[qid] for qid in question_dimension_map])
		self.qid_set = qid_set

	def get_qid(self, question: QID or SQuestion) -> QID:
		return self.qid_resolver[question]

	def get_aid(
		self,
		question: QID or SQuestion,
		answer: AID or SChoice
	) -> AID:
		qid = self.qid_resolver[question]
		return self.aid_resolver[qid][answer]

	def convert_response_to_vector(
		self,
		response: Dict[QID, AID]
	) -> np.ndarray:
		vector_list = []
		for qid in self.question_ids_ordered():
			vector_list.extend(self.get_answer_vector(qid, response))
		return np.array(vector_list)

	def get_answer_vector(
		self,
		qid: QID,
		response: Dict[QID, AID]
	) -> List[int]:
		if response.get(qid, None) is None:
			return [0 for _ in range(self.question_dimension_map[qid])]
		return self.aid_vector_map[qid][response[qid]]

	def question_ids_ordered(self) -> List[QID]:
		return sorted([qid for qid in self.question_ids()])

	def question_ids(self) -> Iterable[QID]:
		for qid in self.qid_set:
			yield qid

	def question_count(self) -> int:
		return len(self.qid_set)

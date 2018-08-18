from typing import Iterable, Dict, Set
from app.classifier.custom_types import SQuestion, SChoice, QID, AID
import numpy as np
import app.db.database as database
from app.utils.resolver_util import ValueResolver

# todo - implement all the methods in this class as they are not implemented
class QuestionAnswerManager:
	def __init__(self) -> None:
		self.qid_resolver: ValueResolver[QID or SQuestion, QID] = None
		self.aid_resolver: Dict[QID, ValueResolver[AID or SChoice, AID]] = None
		self.input_dimension: int = None
		self.qid_set: Set[QID] = None
		self.setup()

	def get_qid(self, question: QID or SQuestion) -> QID:
		raise NotImplementedError

	def get_aid(self, question: QID or SQuestion, answer: AID or SChoice) -> AID:
		qid = self.qid_resolver[question]
		return self.aid_resolver[qid][answer]

	def convert_response_to_vector(self, response: Dict[QID, AID or None]) -> np.ndarray:
		raise NotImplementedError

	def question_ids(self) -> Iterable[QID]:
		for qid in self.qid_set:
			yield qid

	def setup(self) -> None:
		raise NotImplementedError

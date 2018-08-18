from typing import Iterable, Dict
from app.classifier.custom_types import (
	SQuestion,
	SChoice,
	SCourseNumber,
	SCourse,
	QID,
	AID,
	CID,
)
from app.classifier.course_manager import CourseManager
from app.classifier.question_answer_manager import QuestionAnswerManager
import numpy as np


class DataManager:
	def __init__(self):
		self._input_dim, self._output_dim = None, None
		self.response_choices: Dict[QID, AID] = {}
		self.cm = CourseManager()
		self.qam = QuestionAnswerManager()

	def input_dimension(self) -> int:
		return self.qam.input_dimension

	def output_dimension(self) -> int:
		return self.cm.course_count

	def set_answer(
		self,
		question: QID or SQuestion,
		choice: AID or SChoice,
	) -> None:
		self.response_choices[self.qam.get_qid(question)] = self.qam.get_aid(question, choice)

	def store_response(
		self,
		course: CID or SCourse or SCourseNumber = None,
	) -> None:
		self.assert_all_questions_answered()
		raise NotImplementedError

	def assert_all_questions_answered(self):
		not_answered = [
			qid for qid in self.question_ids()
			if qid not in self.response_choices
		]
		assert len(not_answered) == 0, (
			"questions with question ids [%s] aren't answered "
			"yet" % ",".join([str(qid) for qid in not_answered])
		)

	def refresh_response(self):
		raise NotImplementedError

	def vector_from_response(self) -> np.ndarray:
		return self.qam.convert_response_to_vector(self.response_choices)

	def load_training_data(self):
		pass

	def question_ids(self) -> Iterable[QID]:
		yield from self.qam.question_ids()

	def course_ids(self) -> Iterable[CID]:
		yield from self.cm.course_ids()


if __name__ == '__main__':
	a = DataManager()
	for cid in a.course_ids():
		print(a.cm.get_course_bundle(cid))

import os
import utils
import numpy as np
from typing import Tuple, List, Dict
from custom_types import \
	Vector, RowVector, QuestionID, AnswerSetID, QuestionSetID, MappingSetID, \
	SAnswer, SCourseNumber, SCourse


class QuestionManager:
	"""
	helps with various things related to questions
	"""

	def __init__(self, question_set_id: QuestionSetID) -> None:
		self.qsid = question_set_id
		self.order, self.map = [], {}
		self.setup()

	def setup(self) -> None:
		"""
		populate both the order and the map
		"""
		file_path = utils.get_data_format_path() + '/q-%s.txt' % self.qsid
		with open(file_path, 'r', encoding='utf-8') as question_file:
			lines = question_file.readlines()
			question_groups = []
			for index in range(0, len(lines), 3):
				question_groups.append([
					line.strip('\n') for line in lines[index:index + 3]
				])
			# sometimes the last line has a newline character to nothing
			if len(question_groups[-1]) == 1:
				question_groups.pop(-1)
			for question_id, question, answers in question_groups:
				self.order.append(question_id)
				self.map[question_id] = {
					'question': question,
					'choices': [
						utils.clean_string(answer)
						for answer in answers.split(',')
					]
				}
			self.order = sorted(self.order)

	def question(self, question_id: QuestionID) -> dict:
		return self.map[question_id]['question']

	def question_answer_index(self, question_id: QuestionID, answer: SAnswer) -> int:
		return self.map[question_id]['choices'].index(utils.clean_string(answer))

	def __iter__(self):
		for question_id in self.order:
			yield question_id

	def question_answers_for_question_id(self, question_id: QuestionID) -> SAnswer:
		return self.map[question_id]['choices']


class AnswerManager:
	def __init__(
			self,
			question_set_id: QuestionSetID,
			mapping_set_id: MappingSetID) -> None:
		self.qsid = question_set_id
		self.msid = mapping_set_id
		self.order, self.map, self.position_boundaries = [], {}, {}
		self.setup()

	def setup(self) -> None:
		"""
		populate both the map
		"""
		file_path = os.path.join(
			utils.get_data_format_path(),
			'm-%s-%s.txt' % (self.qsid, self.msid)
		)
		with open(file_path, 'r', encoding='utf-8') as mapping_file:
			# get rid of comments
			lines = [line for line in mapping_file.readlines() if line[0] != '#']
			mapping_groups = []
			for index in range(0, len(lines), 2):
				mapping_groups.append([
					line.strip('\n') for line in lines[index:index + 2]
				])
			# sometimes the last line has a newline character to nothing
			if len(mapping_groups[-1]) == 1:
				mapping_groups.pop(-1)
			for question_id, map_vector in mapping_groups:
				# map then to row vectors
				self.map[question_id] = [
					np.array([[int(integer) for integer in vector.split(',')]])
					for vector in map_vector.split(';')
				]
				self.order.append(question_id)
			self.order = sorted(self.order)
			# map the starting position for each id
			index = 0
			for question_id in self:
				left = index
				right = index + self.get_dimensions_for_question(question_id)
				self.position_boundaries[question_id] = (left, right)
				index = right

	def get_dimensions_for_question(self, question_id: QuestionID) -> int:
		return self.map[question_id][0].shape[1]

	def question_boundaries(self, question_id: QuestionID) -> Tuple[int, int]:
		return self.position_boundaries[question_id]

	def question_vector(self, question_id: QuestionID, index: int) -> RowVector:
		return self.map[question_id][index]

	def __iter__(self):
		for question_id in self.order:
			yield question_id


class DataParser:
	"""
	this class has the following goals:
	- parse the data from the data folder using the question id and
	mapping set id by converting them into vectors to use by classifier
	- parse incoming data from online and convert them into vectors to use
	by classifier
	- take incoming data and store them with the appropriate data path
	"""

	def __init__(
			self,
			question_set_id: QuestionSetID,
			mapping_set_id: MappingSetID) -> None:
		self.qsid = question_set_id
		self.msid = mapping_set_id
		# map tuples if (qid, answer) to a vector representation of that answer
		# qm and am stand for question manager and answer manager respectively
		self.base_answer_vector, self.qm, self.am = None, None, None
		self.answer_vector, self.answer_map = None, None
		self.courses, self.course_index_map, self.course_number_map = None, {}, {}
		self.setup()

	def setup(self) -> None:
		questions = QuestionManager(self.qsid)
		answers = AnswerManager(self.qsid, self.msid)
		dimensions = 0
		for question_id in questions:
			dimensions += answers.get_dimensions_for_question(question_id)
		self.base_answer_vector = np.zeros((1, dimensions))
		self.qm, self.am = questions, answers
		self.refresh_answer()
		self.populate_courses()

	def refresh_answer(self) -> None:
		self.answer_vector = self.base_answer_vector.copy()
		self.answer_map = {}

	def populate_courses(self) -> None:
		if self.courses is None:
			self.courses, self.course_number_map = DataParser.load_courses()

	@staticmethod
	def load_courses() -> Tuple[List, Dict[SCourse, SCourseNumber]]:
		path = utils.get_data_format_path() + '/courses.txt'
		with open(path, 'r', encoding='utf-8') as course_file:
			courses, course_number_map = [], {}
			for line in course_file.readlines():
				course_bundle = line.split(':')
				course_number = utils.clean_string(course_bundle[0])
				course_name = utils.clean_string(course_bundle[1].strip('\n'))
				courses.append(SCourse(course_name))
				course_number_map[course_name] = SCourseNumber(course_number)
			return sorted(courses), course_number_map

	def __iter__(self) -> QuestionID:
		for question_id in self.qm:
			yield question_id

	def load_specific_training_data(
			self,
			data_id: AnswerSetID) -> Tuple[RowVector, RowVector]:
		return self.parse_data_file(
			os.path.join(
				self.get_data_dir_path(),
				'd-%s-%s.txt' % (self.qsid, data_id)
			)
		)

	def load_training_data(self) -> Tuple[Vector, Vector]:
		"""
		Load the training. The output, per keras documentation, is a
		list of vector for the data and a list of vectors for labels.
		The vectors are in the form of row vectors. So, in that sense,
		using a 2d numpy array is equivalent. For our sake, the labels
		are also large vectors.
		"""
		dir_path = self.get_data_dir_path()
		if not os.path.exists(dir_path):
			os.makedirs(dir_path)
			raise ValueError('no data recorded for this question set yet')
		# list every files in this directory
		data_list, label_list = [], []
		for data_file_name in os.listdir(dir_path):
			data, label = self.parse_data_file(os.path.join(
				dir_path,
				'%s' % data_file_name
			))
			data_list.append(data)
			label_list.append(label)
		return np.vstack(data_list), np.vstack(label_list)

	def get_data_dir_path(self) -> str:
		return os.path.join(
			'/',
			__file__.strip('/data_parsing.py'),
			'data',
			'd-%s' % self.qsid,
		)

	def parse_data_file(self, data_path: str) -> Tuple[RowVector, RowVector]:
		with open(data_path, 'r', encoding='utf-8') as data_file:
			lines = [line.strip('\n') for line in data_file.readlines()]
			course, vector_map = lines[0], {}
			for i in range(1, len(lines), 2):
				question_id, answer = lines[i:i + 2]
				vector = self.am.question_vector(
					question_id,
					self.qm.question_answer_index(question_id, answer)
				)
				vector_map[question_id] = vector
			data_vector = self.create_data_vector_from_map(vector_map)
			label = self.course_vector(course)
			return data_vector, label

	def create_data_vector_from_map(
			self,
			vector_map: Dict[QuestionID, RowVector]) -> RowVector:
		return np.hstack([vector_map[question_id] for question_id in self])

	def course_vector(self, course: SCourse) -> RowVector:
		return Vector.one_hot_repr(len(self.courses), self.course_index(course))

	def course_index(self, course: SCourse) -> int:
		self.course_index_map[course] = self.course_index_map.get(
			course,
			self.courses.index(course)
		)
		return self.course_index_map[course]

	def course_number(self, course: SCourse) -> int:
		return self.course_number_map[course]

	def set_answer(self, question_id: QuestionID, answer: SAnswer) -> None:
		left, right = self.am.question_boundaries(question_id)
		answer_vector = self.am.question_vector(
			question_id,
			self.qm.question_answer_index(question_id, answer)
		)
		self.answer_vector[:, left:right] = answer_vector
		self.answer_map[question_id] = answer

	def get_answer_vector(self) -> np.ndarray:
		return self.answer_vector.copy()

	def input_dimension(self) -> int:
		return self.base_answer_vector.shape[1]

	def output_dimension(self) -> int:
		return len(self.courses)

	def store_answer(self, course: SCourse) -> None:
		self.assert_can_store_response(course)

		data_dir_path = self.get_data_dir_path()
		data_ids = set(
			data_file_name[6:].strip('.txt')
			for data_file_name in os.listdir(data_dir_path)
		)
		data_id = utils.generate_unique_id(data_ids, utils.generate_data_id)
		data_path = os.path.join(data_dir_path, 'd-%s-%s.txt' % (self.qsid, data_id))

		with open(data_path, 'w', encoding='utf-8') as data_file:
			data_file.writelines([course + '\n'])
			for question_id in self:
				data_file.writelines([
					question_id + '\n',
					self.answer_map[question_id] + '\n'
				])
			data_file.close()

	def assert_can_store_response(self, course: SCourse):
		self.assert_is_valid_course(course)
		self.assert_has_answered_everything()

	def assert_is_valid_course(self, course: SCourse) -> None:
		assert course in self.courses, 'invalid course -> %s' % course

	def assert_has_answered_everything(self) -> None:
		err_msg = ''.join([
			'all questions need to be answered',
			'to be stored -> %s is not answered'
		])
		for question_id in self:
			assert self.answer_map.get(
				question_id,
				None
			) is not None, err_msg % QuestionID(question_id)

	def get_course_rankings(
			self,
			prediction: RowVector) -> List[Tuple[SCourseNumber, SCourse, float]]:
		course_ranking = [
			(
				self.course_number_map[course],
				course,
				prediction[0, self.course_index(course)]
			)
			for course in self.courses
		]
		return sorted(course_ranking, key=lambda tup: -tup[2])


if __name__ == '__main__':
	dp = DataParser(QuestionSetID('314'), MappingSetID('35780'))
	# d = dp.load_training_data()
	# print(dp.course_vector(SCourse('Biology')))
	# print(dp.course_index(SCourse('Biology')))
	# print(dp.qm.question_answers_for_question_id(qid))
	# print(dp.store_answer(SCourse('Aeronautics and Astronautics')))
	d, l = dp.load_training_data()
	print(d)
	print(l)
import os
import utils
import numpy as np
from typing import List, Tuple, Any, Dict
from custom_types import \
	RowVector, QuestionSetID, QuestionID, MappingSetID, AnswerSetID, \
	SAnswer, SCourse, SCourseNumber
from data_parsing import DataParser
# for machine learning
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


class Classifier:
	"""
	helps us make both predictions and learning for our course classifications
	"""

	def __init__(
			self,
			question_set_id: QuestionSetID,
			mapping_set_id: MappingSetID) -> None:
		self.qsid = question_set_id
		self.msid = mapping_set_id
		self.parser = DataParser(self.qsid, self.msid)
		self.data = None
		self.classifier = None
		self.setup_classifier(
			nn_layer_units=((100, 'relu'), (50, 'relu')),
			optimizer=Adam()
		)

	def setup_classifier(
			self,
			nn_layer_units: Tuple[Tuple[int, str], ...] = ((100, 'relu'),),
			optimizer: Any = 'sgd') -> None:
		"""
		setup the classifier by adding all given hidden layers and using
		input dim and output dim from self.parser
		:param nn_layer_units:
			A tuple containing a sequence of tuples each containing an int
			that specifies the number of hidden units and a string that
			specifies the activation to use
		:param optimizer:
			optimization method for NN
		"""
		first_hidden_layer_unit_count, activation = nn_layer_units[0]
		self.classifier = Sequential()
		self.classifier.add(Dense(
			units=first_hidden_layer_unit_count,
			activation=activation,
			input_dim=self.parser.input_dimension())
		)
		# add all the hidden layers, then ha
		for hidden_layer_unit_count, activation in nn_layer_units[1:]:
			self.classifier.add(Dense(
				units=hidden_layer_unit_count,
				activation=activation
			))
		self.classifier.add(Dense(
			units=self.parser.output_dimension(),
			activation='softmax')
		)
		self.classifier.compile(
			loss='categorical_crossentropy',
			optimizer=optimizer,
			metrics=['accuracy']
		)

	def store_training_data(
			self,
			answer_map: Dict[QuestionID, SAnswer],
			course: SCourse) -> None:
		"""
		Store the training data labeled with this course number
		Note:
			this will throw an error if some key in the dictionary
			are missing. That is intentional.
		"""
		for question_id in self.parser:
			self.parser.set_answer(question_id, answer_map[question_id])
		self.parser.store_answer(course)
		self.parser.refresh_answer()

	def predict_ranking_from_data_file(
			self,
			data_id: AnswerSetID,
			verbose: int = 0) -> List[Tuple[SCourseNumber, SCourse, float]]:
		"""
		returns an ordered list of predicted courses, ranging from
		best course prediction to worst
		"""
		return self.parser.get_course_rankings(
			self.predict_from_data_file(data_id, verbose)
		)

	def predict_from_data_file(
			self,
			data_id: AnswerSetID,
			verbose: int = 0) -> RowVector:
		"""
		see Classifier.predict
		"""
		vector, _ = self.parser.load_specific_training_data(data_id)
		return self.predict(vector, verbose=verbose)

	def answer_map_to_vector(
			self,
			answer_map: Dict[QuestionID, SAnswer]) -> RowVector:
		"""
		see Classifier.predict
		Note:
			this will throw an error if some key in the dictionary
			are missing. That is intentional.
		"""
		for question_id in self.parser:
			self.parser.set_answer(question_id, answer_map[question_id])
		return self.parser.get_answer_vector()

	def predict_ranking(
			self,
			answer_vector: RowVector,
			verbose: int = 0) -> List[Tuple[SCourseNumber, SCourse, float]]:
		"""
		returns an ordered list of predicted courses, ranging from
		best course prediction to worst
		"""
		return self.parser.get_course_rankings(
			self.predict(answer_vector, verbose)
		)

	def predict(self, answer_vector: RowVector, verbose: int = 0) -> RowVector:
		"""
		outputs a dictionary that maps the probabilities of each major
		based on these choices
		:param answer_vector:
			a numpy column vector
		:param course:
			the actual course for this answer_vector. this will mostly be none
		:return:
			a ColumnVector that represent the probability for various courses
			as can be seen in DataParser
		"""
		return self.classifier.predict(answer_vector, verbose=verbose)

	def train(
			self,
			epochs: int = 5,
			batch_size: int = 32,
			verbose_mode: int = 1) -> None:
		"""
		train the classifier based on the data that we currently have
		"""
		if self.data is None:
			self.data, self.label = self.parser.load_training_data()
		self.classifier.fit(
			self.data,
			self.label,
			epochs=epochs,
			batch_size=batch_size,
			verbose=verbose_mode
		)


if __name__ == '__main__':
	a = Classifier(QuestionSetID('314'), MappingSetID('35780'))
	a.train(verbose_mode=0)
	prediction = a.predict_ranking_from_data_file(AnswerSetID('p68n6s'))
	courses = ','.join([str(tuple(repr(e) for e in p[:-1])) for p in prediction])
	print(courses)
	for p in prediction:
		print(p)
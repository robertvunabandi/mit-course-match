import os
import utils
import numpy as np
from typing import List, Tuple, Any, Dict
from custom_types import \
	RowVector, QuestionSetID, QuestionID, MappingSetID, AnswerSetID, \
	SChoice, SQuestion, SCourseNumber, SCourse, QID, AID, RID, CID, QSID, MSID
from data_parsing import DataManager
# for machine learning
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam, SGD
from keras.activations import relu, softmax


class Classifier:
	"""
	helps us make both predictions and learning for our course classifications
	"""

	def __init__(
			self,
			qsid: QSID,
			msid: MSID,
			nn_hidden_layers=((100, relu), (50, relu))) -> None:
		self.qsid = qsid
		self.msid = msid
		self.data_manager = DataManager(self.qsid, self.msid)
		self.data = None
		self._classifier = None
		self.setup_classifier(nn_hidden_layers=nn_hidden_layers)

	def setup_classifier(
			self,
			nn_hidden_layers: Tuple[Tuple[int, str or Any], ...]
			) -> None:
		"""
		setup the _classifier by adding all given hidden layers and using
		input dim and output dim from self.data_manager
		:param nn_hidden_layers:
			A tuple containing a sequence of tuples each containing an int
			that specifies the number of hidden units and a string that
			specifies the activation to use
		"""
		first_hidden_layer_unit_count, activation = nn_hidden_layers[0]
		self._classifier = Sequential()

		self._classifier.add(Dense(
			units=first_hidden_layer_unit_count,
			activation=activation,
			input_dim=self.data_manager.input_dimension
		))
		for hidden_layer_unit_count, activation in nn_hidden_layers[1:]:
			self._classifier.add(Dense(
				units=hidden_layer_unit_count,
				activation=activation
			))
		self._classifier.add(Dense(
			units=self.data_manager.output_dimension,
			activation=softmax
		))

		self._classifier.compile(
			loss='categorical_crossentropy',
			optimizer=Adam(),
			metrics=['accuracy']
		)

		self.train()

	def train(
			self,
			epochs: int = 5,
			batch_size: int = 32,
			verbose_mode: int = 1) -> None:
		"""
		train the _classifier based on the data that we currently have
		"""
		if self.data is None:
			self.data, self.label = self.data_manager.load_training_data()
		if self.data is not None and self.label is not None:
			self._classifier.fit(
				self.data,
				self.label,
				epochs=epochs,
				batch_size=batch_size,
				verbose=verbose_mode
			)

	def store_training_data(
			self,
			answer_map: Dict[QID or SQuestion, AID or SChoice],
			cid_identifier: SCourse or CID or SCourseNumber = None) -> None:
		"""
		Store the training data labeled with this course number
		Note:
			this will throw an error if some key in the dictionary
			are missing. That is intentional.
		"""
		for qid in self.data_manager.qa_manager.question_ids():
			self.data_manager.set_answer(qid, answer_map[qid])
		self.data_manager.store_responses(cid_identifier)
		self.data_manager.refresh_responses()

	def predict_course_from_rid(
			self,
			rid: RID) -> List[Tuple[SCourseNumber, SCourse, float]]:
		# load the response
		# run through classifier to predict (ensure classifier is trained)
		# then rank the output
		pass

	def predict_ranking_from_data_file(
			self,
			data_id: AnswerSetID,
			verbose: int = 0) -> List[Tuple[SCourseNumber, SCourse, float]]:
		"""
		returns an ordered list of predicted courses, ranging from
		best course prediction to worst
		"""
		return self.data_manager.get_course_rankings(
			self.predict_from_data_file(data_id, verbose)
		)

	def predict_from_data_file(
			self,
			data_id: AnswerSetID,
			verbose: int = 0) -> RowVector:
		"""
		see Classifier.predict
		"""
		vector, _ = self.data_manager.load_specific_training_data(data_id)
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
		for question_id in self.data_manager:
			self.data_manager.set_answer(question_id, answer_map[question_id])
		return self.data_manager.get_answer_vector()

	def predict_ranking(
			self,
			answer_vector: RowVector,
			verbose: int = 0) -> List[Tuple[SCourseNumber, SCourse, float]]:
		"""
		returns an ordered list of predicted courses, ranging from
		best course prediction to worst
		"""
		return self.data_manager.get_course_rankings(
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
		return self._classifier.predict(answer_vector, verbose=verbose)


if __name__ == '__main__':
	a = Classifier(QuestionSetID('314'), MappingSetID('35780'))
	a.train(verbose_mode=0)
	prediction = a.predict_ranking_from_data_file(AnswerSetID('p68n6s'))
	courses = ','.join([str(tuple(repr(e) for e in p[:-1])) for p in prediction])
	print(courses)
	for p in prediction:
		print(p)

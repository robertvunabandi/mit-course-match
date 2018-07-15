import os
import utils
import numpy as np
from typing import List, Tuple, Any, Dict
import database
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
			qsid: QSID or int,
			msid: MSID or int,
			nn_hidden_layers=((100, relu), (50, relu))) -> None:
		self.qsid = QSID(qsid)
		self.msid = MSID(msid)
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

	def predict_from_rid(
			self,
			rid: RID) -> List[Tuple[SCourseNumber, SCourse, float]]:
		response: Dict[QID, AID] = database.load_response(rid)
		vector: np.ndarray = self.data_manager.vector_from_responses(response)
		return self.predict_ranking(vector)

	def predict_ranking(
			self,
			vector: np.ndarray,
			verbose: int = 0) -> List[Tuple[SCourseNumber, SCourse, float]]:
		"""
		returns an ordered list of predicted courses, ranging from
		best course prediction to worst
		:param vector: A vector that has the shape (1, self.data_manager.input_dimension)
		:param verbose: the verbosity level when making the prediction
		:return:
		"""
		return self.get_course_rankings(
			self._classifier.predict(vector, verbose=verbose)
		)

	def get_course_rankings(
			self,
			prediction: np.ndarray) -> List[Tuple[SCourseNumber, SCourse, float]]:
		# todo - implement this after learning what prediction looks like
		print(prediction)
		raise NotImplementedError


if __name__ == '__main__':
	a = Classifier(QSID(3), MSID(2))
	a.train(verbose_mode=0)
	prediction = a.predict_from_rid(RID(1))
	courses = ','.join([str(tuple(repr(e) for e in p[:-1])) for p in prediction])
	print(courses)
	for p in prediction:
		print(p)

from typing import Dict, Tuple
from app.classifier.custom_types import SCourseNumber, SCourse, CID, Vector
from app.utils.resolver_util import ValueResolver
import app.db.database as database
import numpy as np


class CourseManager:
	def __init__(self) -> None:
		self.cid_to_course: Dict[CID, Tuple[SCourseNumber, SCourse]] = None
		# the index of the course in order will help with matching it with
		# vector prediction at the end
		self.cid_to_index: Dict[CID, int] = None
		self.cid_resolver: ValueResolver[CID or SCourse or SCourseNumber, CID] = None
		self.cid_to_vector: Dict[CID, np.ndarray] = {}
		self.course_count: int = None
		self.setup()

	def setup(self) -> None:
		cid_to_course, cid_resolver, cids = ValueResolver(), {}, []
		for cid_, cn_, course_ in database.load_courses():
			cn, course = SCourseNumber(cn_), SCourse(course_)
			cid = CID(cid_)
			cid_to_course[cid] = (cn, course)
			cid_resolver[[cid, course, cn]] = cid
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
		cid = self.cid(course_identifier)
		if cid in self.cid_to_vector:
			return self.cid_to_vector[cid]
		course_index = self.cid_to_index[cid]
		self.cid_to_vector[cid] = \
			Vector.one_hot_repr(self.course_count, course_index)
		return self.get_course_vector(cid)

	def get_course_bundle(
		self,
		course_identifier: CID or SCourse or SCourseNumber
	) -> Tuple[CID, SCourseNumber, SCourse]:
		cid = self.cid(course_identifier)
		cn, course = self.cid_to_course[cid]
		return cid, cn, course

	def get_course_index(
		self,
		course_identifier: CID or SCourse or SCourseNumber
	) -> int:
		return self.cid_to_index[self.cid(course_identifier)]

	def cid(self, course_identifier: CID or SCourse or SCourseNumber) -> CID:
		return self.cid_resolver[course_identifier]

	def course_ids(self) -> CID:
		for cid in self.cid_to_course:
			yield cid

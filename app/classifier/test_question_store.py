import unittest
import app.classifier.question_store as qs


class TestQuestionStore(unittest.TestCase):
	def test_assert_valid_inputs_01_should_raise(self):
		try:
			qs.QuestionStore.assert_valid_inputs(None, None)
			self.fail("should have failed because of bad inputs")
		except AssertionError:
			pass

	def test_assert_valid_inputs_02_should_raise(self):
		try:
			qs.QuestionStore.assert_valid_inputs('hello', ['dug', [1, 4]])
			self.fail("should have failed because of bad inputs")
		except AssertionError:
			pass

	def test_assert_valid_inputs_03_should_raise(self):
		try:
			qs.QuestionStore.assert_valid_inputs('chocolate', [('yes', [1, 2])])
			self.fail("should have failed because need at least 2 choices")
		except AssertionError:
			pass

	def test_assert_valid_inputs_04_should_raise(self):
		m = "should have failed because inconsistent dimensions across choices"
		try:
			qs.QuestionStore.assert_valid_inputs(
				'chocolate',
				[('yes', [1, 2]), ('no', [1, 2, 5])]
			)
			self.fail(m)
		except AssertionError:
			pass

	def test_assert_valid_inputs_05_should_raise(self):
		try:
			qs.QuestionStore.assert_valid_inputs(
				'chocolate',
				[('yes', [1, 2]), (None, [1, 2])]
			)
			self.fail("should have failed because choice is None")
		except AssertionError:
			pass

	def test_assert_valid_inputs_01_should_pass(self):
		try:
			qs.QuestionStore.assert_valid_inputs(
				'chocolate',
				[('yes', [1, 2]), ('no', [1, -1])]
			)
		except AssertionError as e:
			print(e)
			self.fail("should not fail")

	def test_assert_valid_inputs_02_should_pass(self):
		try:
			qs.QuestionStore.assert_valid_inputs(
				'chocolate',
				[('yes', [1, 2.1, 3.5]), ('no', [1, -1, 0.14])]
			)
		except AssertionError as e:
			print(e)
			self.fail("should not fail")


if __name__ == '__main__':
	unittest.main()

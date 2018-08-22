"""
since this package is about strings, we break the descriptive naming
convention. Use "s" for strings
"""
from typing import Any


def is_string(s: Any) -> bool:
	return type(s) == str


def is_string_integer(s: str) -> bool:
	if type(s) != str:
		return False
	try:
		int(s)
		return True
	except ValueError:
		return False


def is_csv_string_vector(s: str) -> bool:
	if type(s) != str:
		return False
	return all([is_string_integer(sub_s) for sub_s in s.split(',')])


def get_csv_string_dimension(s: str) -> int:
	assert is_csv_string_vector(s) is True, "argument is not csv string"
	return len(s.split(','))


def clean_string(s: str) -> str:
	"""
	remove white spaces at beginning and end
	"""
	assert type(s) == str, "expecting s, instead got %s" % repr(type(s))
	if len(s) == 0:
		return s
	if s[0] == ' ':
		return clean_string(s[1:])
	if s[-1] == ' ':
		return clean_string(s[:-1])
	return s

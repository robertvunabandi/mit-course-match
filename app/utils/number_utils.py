"""
since this package is about numbers, we break the descriptive naming
convention. Use "i" for integers and "f" for floats/doubles
"""
from typing import Any


FLOAT_DELTA = 0.0000001


def is_integer(i: Any) -> bool:
	return type(i) == int


def is_float(i: Any) -> bool:
	return is_integer(i) or type(i) == float


def assert_valid_db_id(i: Any, idtype: str = None) -> None:
	idtype = 'id' if idtype is None else str(idtype)
	assert isinstance(i, int), \
		'%s must be an instance of integer. Got %s' % (idtype, repr(type(i)))


def is_integer_in_range_exclusive(i: int, min_: int, max_: int) -> bool:
	msg = "expecting integer. Instead got %s of type %s"
	assert is_integer(i), msg % (repr(i), repr(type(i)))
	assert is_integer(min_), msg % (repr(min_), repr(type(min_)))
	assert is_integer(max_), msg % (repr(max_), repr(type(max_)))
	return min_ < i < max_


def is_integer_in_range_inclusive(i: int, min_: int, max_: int) -> bool:
	return is_integer_in_range_exclusive(i, min_ - 1, max_ + 1)


def is_in_range_exclusive(f: float, min_: float, max_: float) -> bool:
	msg = "expecting float. Instead got %s of type %s"
	assert is_float(f), msg % (repr(f), repr(type(f)))
	assert is_float(min_), msg % (repr(min_), repr(type(min_)))
	assert is_float(max_), msg % (repr(max_), repr(type(max_)))
	return min_ < f < max_


def is_in_range_inclusive(f: float, min_: float, max_: float) -> bool:
	return is_in_range_exclusive(f, min_ - FLOAT_DELTA, max_ + FLOAT_DELTA)

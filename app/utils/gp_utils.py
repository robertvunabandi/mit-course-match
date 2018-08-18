"""
GP stands for General Purpose
"""
from typing import Any


def none_raise(arg: Any, msg: str = None) -> None:
	assert arg is not None, \
		"argument given (%s) is null" % str(arg) if msg is None else msg

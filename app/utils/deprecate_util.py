import warnings as _warnings
import inspect as _inspect
import functools as _functools
from typing import Callable, Any


def deprecated(reason: Callable or str = None) -> Any:
	if _inspect.isclass(reason) or _inspect.isfunction(reason):
		func = reason
		deprecated_message = "Call to deprecated {type} {name}".format(
			type="class" if _inspect.isclass(func) else "function",
			name=func.__name__,
		)

		@_functools.wraps(func)
		def new_func(*args, **kwargs) -> Any:
			_warnings.simplefilter('always', DeprecationWarning)
			_warnings.warn(
				deprecated_message,
				category=DeprecationWarning,
				stacklevel=2
			)
			_warnings.simplefilter('default', DeprecationWarning)
			return func(*args, **kwargs)

		return new_func

	if type(reason) == str:
		def real_deprecated_decorator(func: Callable) -> Any:
			deprecated_message_reason = \
				"Call to deprecated {type} {name} ({reason})".format(
					type="class" if _inspect.isclass(func) else "function",
					name=func.__name__,
					reason=reason,
				)

			@_functools.wraps(func)
			def new_func_with_reason(*args, **kwargs) -> Any:
				_warnings.simplefilter('always', DeprecationWarning)
				_warnings.warn(
					deprecated_message_reason,
					category=DeprecationWarning,
					stacklevel=2
				)
				_warnings.simplefilter('default', DeprecationWarning)
				return func(*args, **kwargs)

			return new_func_with_reason

		return real_deprecated_decorator
	raise TypeError(
		"neither a method, class, or string was given to the deprecated "
		"decorator. Got type %s with value %s" %
		(repr(type(reason)), repr(reason))
	)

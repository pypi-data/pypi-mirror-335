from abc import ABC as _ABC, abstractmethod as _abstractmethod
from typing import Callable as _Callable
from functools import wraps as _wraps
from io import StringIO as _StringIO
from typing import Any as _Any
from time import time as _time

# ANSI escape sequences
_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_STOP = "\033[0m"

# Levels of messages
_ERROR = "ERROR"
_WARN = "WARN"
_OK = "OK"

# Dictionary for mapping statuses and colors
_COLORS = {
    _ERROR: _RED,
    _WARN: _YELLOW,
    _OK: _GREEN
}   

def _write(text: str) -> None:
    """
    A function to print text, replacing some strings with ANSI escape sequences.

    Args:
        text: str
    Returns: None
    """

    mapping = {
        "<red>": _RED,
        "<green>": _GREEN,
        "<blue>": _BLUE,
        "<yellow>": _YELLOW,
        "<stop>": _STOP
    }

    for key, value in mapping.items():
        text = text.replace(key, value)

    print(text)

def patch(target: str, replacement: _Any) -> _Callable:
    """
    Replace a target value with a replacement for the run time of a function.

    Args: 
        target: str
        replacement: Any
    Returns: Callable
    """

    def decorator(func: _Callable) -> _Callable:
        @_wraps(func)
        def wrapper(*args: _Any, **kwargs: _Any) -> _Any:
            module_name, object_name = target.rsplit('.', 1)
            module = __import__(module_name, fromlist=[object_name])
            original = getattr(module, object_name)

            try:
                setattr(module, object_name, replacement)
                kwargs[f"mock_{object_name}"] = replacement
                _ = func(*args, **kwargs)
            
            finally:
                setattr(module, object_name, original)

            return _
        return wrapper
    return decorator

class _TestCase(_ABC):
    """
    Base class which ImperativeTestCase and DeclarativeTestCase inherit from.
    Inherits: ABC
    """

    _PASS_SELF_TO_TESTS = ...

    def __init__(self, name: str) -> None:
        self._name = name

    def set_up(self) -> None: 
        """
        This function is called before each test.

        Args: None
        Returns: None
        """
        pass

    def tear_down(self) -> None:
        """
        This function is called after each test.

        Args: None
        Returns: None
        """
        pass

    @_abstractmethod
    def _test_holder(self) -> dict: ...

    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, new: str) -> None:
        self._name = new

    @name.deleter
    def name(self) -> None:
        self._name = None

    @patch("sys.stdout", _StringIO())
    @patch("sys.stdin", _StringIO())
    @patch("sys.stderr", _StringIO())
    def run_test(self, test: _Callable, mock_stdout: _StringIO, mock_stdin: _StringIO, mock_stderr: _StringIO) -> tuple[str, str | _Any]:
        """
        Runs a test and returns the status and result (or message).

        Args: 
            test: _Callable
        Returns: None
        """

        try:
            _ = None
            self.set_up()

            if self._PASS_SELF_TO_TESTS:
                _ = test(self)

            else:
                _ = test()

            self.tear_down()
        
        except Warning as warn:
            return _WARN, warn
        
        except Exception as error:
            return _ERROR, error
        
        else:
            return _OK, _
        
    def run(self) -> None:
        """
        Run all tests.

        Args: None
        Returns: None
        """

        _write(f"<green>Running {self}<stop>\n")
        tests = {}
        start = _time()
        items = list(self._test_holder().items())

        for name, attr in items:
            if callable(attr) and (name.startswith("test") or name.startswith("test_")):
                result = self.run_test(attr)
                tests[name] = result
                _write(f"Test <blue>{name}<stop>: {_COLORS.get(result[0])}{result[1]}<stop>")

        end = _time()
        oks = warns = errors = 0

        for status in tests.values():
            status = status[0]

            if status == _OK:
                oks += 1

            elif status == _WARN:
                warns += 1

            elif status == _ERROR:
                errors += 1

        _write(f"\nRan <blue>{len(self)} {"tests" if self.get_tests() != 1 else "test"}<stop> in <blue>{(end - start):.6f} seconds<stop>")
        _write(f"<green>{oks}<stop> {"tests" if oks != 1 else "test"} <green>passed<stop>")
        _write(f"<yellow>{warns}<stop> {"tests" if warns != 1 else "test"} <yellow>warned<stop>")
        _write(f"<red>{errors}<stop> {"tests" if errors != 1 else "test"} <red>failed<stop>")

    @_abstractmethod
    def __str__(self) -> str: ...
    
    def __repr__(self) -> str:
        return str(self)
    
    def __int__(self) -> int:
        return self.get_tests()
    
    def __len__(self) -> int:
        return self.get_tests()
    
    def __float__(self) -> float:
        return float(int(self))
    
    def get_tests(self) -> int:
        output = 0
        items = list(self._test_holder().items())

        for name, attr in items:
            if callable(attr) and name.startswith("test") or name.startswith("test_"):
                output += 1

        return output

    def assert_equal(self, obj1: _Any, obj2: _Any) -> None:
        assert obj1 == obj2, f"{obj1} is not equal to {obj2}"

    def assert_not_equal(self, obj1: _Any, obj2: _Any) -> None:
        assert obj1 != obj2, f"{obj1} is equal to {obj2}"

    def assert_true(self, obj: _Any) -> None:
        assert obj, f"{obj} is False"

    def assert_false(self, obj: _Any) -> None:
        assert not obj, f"{obj} is True"

    def assert_none(self, obj: _Any) -> None:
        assert obj is None, f"{obj} is not None"

    def assert_not_none(self, obj: _Any) -> None:
        assert obj is not None, f"{obj} is None"

    def assert_in(self, obj: _Any, container: _Any) -> None:
        assert obj in container, f"{obj} not in {container}"

    def assert_not_in(self, obj: _Any, container: _Any) -> None:
        assert obj not in container, f"{obj} is in {container}"

    def assert_returns(self, callable: _Callable, expected: _Any) -> None:
        assert callable() == expected, f"{callable}() does not return {expected}"

    def assert_takes(self, callable: _Callable, expected: float | int) -> None:
        start = _time()
        _ = callable()
        end = _time()
        time = end - start
        assert time == expected, f"{callable}() takes {"more" if time > expected else "less"} time than {expected} seconds"

    def assert_raises(self, exception: type[Exception], callable: _Callable, *args: _Any, **kwargs: _Any) -> None:
        try:
            _ = callable(*args, **kwargs)

        except exception:
            return
        
        except Exception as error:
            raise AssertionError(f"{callable}() does not raise exception {exception.__name__} but rather {error.__class__.__name__}")
        
        else:
            raise AssertionError(f"{callable}() does not raise any exception")
        
    def assert_warns(self, warning: type[Warning], callable: _Callable, *args: _Any, **kwargs: _Any) -> None:
        try:
            _ = callable(*args, **kwargs)

        except warning:
            return
        
        except Warning as warn:
            raise AssertionError(f"{callable}() does not raise warning {warning.__name__} but rather {warn.__class__.__name__}")
        
        except Exception as error:
            raise AssertionError(f"{callable}() does not raise a warning but rather exception {error.__class__.__name__}")
        
        else:
            raise AssertionError(f"{callable}() does not raise any exception or warning")
        
    def assert_almost_equal(self, obj1: _Any, obj2: _Any, places: int = 7) -> None:
        assert round(obj1 - obj2, places) == 0, f"{obj1} and {obj2} are not equal to {places} decimal places"

    def assert_greater(self, obj1: _Any, obj2: _Any) -> None:
        assert obj1 > obj2, f"{obj1} is not greater than {obj2}"

    def assert_greater_than_or_equal(self, obj1: _Any, obj2: _Any) -> None:
        assert obj1 >= obj2, f"{obj1} is not greater than or equal to {obj2}"

    def assert_lesser(self, obj1: _Any, obj2: _Any) -> None:
        assert obj1 < obj2, f"{obj1} is not lesser than {obj2}"

    def assert_lesser_than_or_equal(self, obj1: _Any, obj2: _Any) -> None:
        assert obj1 < obj2, f"{obj1} is not lesser than {obj2}"

class ImperativeTestCase(_TestCase):
    """
    Class for imperative, object-oriented testing.
    Inherits: _TestCase
    """

    _PASS_SELF_TO_TESTS = True

    def __init__(self) -> None:
        return super().__init__(str(self))

    def __str__(self) -> str:
        return f"ImperativeTestCase {self.__class__.__name__} which has {self.get_tests()} {"tests" if self.get_tests() > 1 else "test"}"
    
    def _test_holder(self) -> dict:
        return self.__class__.__dict__

class DeclarativeTestCase(_TestCase):
    """
    Class for declarative testing.
    Inherits: _TestCase
    """

    _PASS_SELF_TO_TESTS = False

    def __init__(self, name: str) -> None:
        super().__init__(name)
    
    def __str__(self) -> str:
        return f"DeclarativeTestCase {self.name} which has {self.get_tests()} {"tests" if self.get_tests() != 1 else "test"}"
    
    def _test_holder(self) -> dict:
        return self.__dict__
    
    def has_test(self, test: _Callable) -> bool:
        name = test.__name__
        if name.startswith("test") or name.startswith("test_"):
            return hasattr(self, name)
    
    def get_test(self, test: _Callable) -> _Any:
        name = test.__name__
        if name.startswith("test") or name.startswith("test_"):
            return getattr(self, name, test)

    def add_test(self, test: _Callable) -> None:
        name = test.__name__
        if name.startswith("test") or name.startswith("test_") or name in {"set_up", "tear_down"}:
            setattr(self, name, test)

    def add_tests(self, *tests: _Callable) -> None:
        for test in tests:
            self.add_test(test)

    def set_test(self, test: _Callable) -> None:
        name = test.__name__
        if name.startswith("test") or name.startswith("test_") or name in {"set_up", "tear_down"}:
            setattr(self, name, test)

    def del_test(self, test: _Callable) -> None:
        name = test.__name__
        if name.startswith("test") or name.startswith("test_"):
            delattr(self, name, test)
